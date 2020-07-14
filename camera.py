import cv2
import numpy as np
import threading
from RecoverPose import recoverPose
import datetime
from cameraCalib import CameraCalibration
from ssd_detection import Detector

global_frame = None


class VideoCamera(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame = self.cap.read()
        # initalise the functional objects
        self.poseRecover = recoverPose(np.identity(3))
        self.calibrater = CameraCalibration()
        self.detector = Detector()
        self.calibFrame = self.cap.read()

        # when calibrate now button is clicked this variable changes
        self.calibNow = False
        # when the auto recalibration toggle is changed then this variable changes
        self.is_auto = False
        # to calibrate after every hour
        self.startingTime = datetime.datetime.now()

        self.min_dist = 150  # (cm)
        self.max_dist = 350  # (cm)

        self.social_distancing_violated = False

    def __del__(self):
        self.cap.release()

    def findWorldDistance(self, point1, point2):
        point1 = np.asarray(point1).reshape((2, 1))
        point2 = np.asarray(point2).reshape((2, 1))

        if(self.calibrater.topViewTransform is None):
            return -1

        temp = np.zeros((3, 1))
        temp[0][0] = point1[0][0]
        temp[1][0] = point1[1][0]
        temp[2][0] = 1

        cornerInTopView = self.calibrater.topViewTransform.dot(temp)
        corner1 = np.zeros((2, 1))
        corner1[0][0] = cornerInTopView[0][0] / cornerInTopView[2][0]
        corner1[1][0] = cornerInTopView[1][0] / cornerInTopView[2][0]

        temp = np.zeros((3, 1))
        temp[0][0] = point2[0][0]
        temp[1][0] = point2[1][0]
        temp[2][0] = 1

        cornerInTopView = self.calibrater.topViewTransform.dot(temp)
        corner2 = np.zeros((2, 1))
        corner2[0][0] = cornerInTopView[0][0] / cornerInTopView[2][0]
        corner2[1][0] = cornerInTopView[1][0] / cornerInTopView[2][0]

        if (self.calibrater.worldRatio):
            pixelDistance = np.sqrt(
                ((corner1[0][0] - corner2[0][0]) ** 2) + ((corner1[1][0] - corner2[1][0]) ** 2))
            worldDistance = self.calibrater.worldRatio * pixelDistance
            return worldDistance
        else:
            return -1

    def markWorldDistance(self, points):
        counter = 0
        for point1 in points:
            for point2 in points:
                if(point1 == point2):
                    continue
                elif(self.findWorldDistance(point1, point2) == -1):
                    continue
                elif(self.findWorldDistance(point1, point2) > self.max_dist):
                    continue
                elif(self.findWorldDistance(point1, point2) < self.min_dist):
                    counter = counter + 1
                    cv2.line(self.frame, point1, point2,
                             (0, 0, 255), thickness=3, lineType=8)
                    cv2.putText(self.frame, "{:.2f}".format(self.findWorldDistance(point1, point2)), point1,
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)
                    continue
                cv2.line(self.frame, point1, point2,
                         (0, 255, 0), thickness=3, lineType=8)
                cv2.putText(self.frame, "{:.2f}".format(self.findWorldDistance(point1, point2)), point1,
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)

        if(counter == 0):
            self.social_distancing_violated = False
        else:
            self.social_distancing_violated = True

    def getCalibData(self, aruco_length, start_calib):
        # To avoid re reading from camera which leads to lagging
        # we are saving the frame as a property
        frame = self.calibFrame

        # code to run the calibration
        # this is a block inside a while loop so is continuously running
        # till calibration is done
        if(start_calib):
            if(self.calibrater.intrinsticDone):
                img = self.calibrater.undistortInput(frame)
                if(not(img is None)):
                    if(self.calibrater.calibrationDone):
                        # print("WORLD RATIO = {:.2f}".format(self.calibrater.worldRatio))
                        topView = self.calibrater.findTopView(frame)
                        if((topView is None)):
                            print("Error in finding top view")
                    else:
                        self.calibrater.calibrate(frame, aruco_length)
                else:
                    print("Intrinstics not found")
            else:
                self.calibrater.findIntrinstics(frame)

    # function to get the frame in the required format for streaming
    # ReCalibration logic controlled here
    def get_frame(self):
        ret, self.frame = self.cap.read()
        output = self.detector.prediction(self.frame)
        df = self.detector.filter_prediction(output, self.frame)
        self.frame = self.detector.draw_boxes(self.frame, df)
        points = self.detector.mid_point(self.frame, df)
        self.markWorldDistance(points)

        # check whether we have to start calibration now
        # starts every hour if is_auto is true and the background has been detected
        # and the calibration is not on currently (if someone uses manual calibration)
        if(self.is_auto and datetime.datetime.now().hour-self.startingTime.hour == 1 and self.poseRecover.backgroundFound and not self.calibNow):
            print("auto calib start")
            self.startingTime = datetime.datetime.now()
            self.calibNow = True
            self.poseRecover.calibrated = False

        # till the bcakground is not found this part runs
        if(not self.poseRecover.backgroundFound):
            self.poseRecover.original_background(self.frame)
        else:
            # if calibrate Now button is clicked this runs
            if(self.calibNow and not self.poseRecover.calibrated):
                self.poseRecover.pose(self.frame)
            if(self.calibNow and self.poseRecover.calibrated):
                # when recalibration is done
                self.calibNow = False
                self.poseRecover.calibrated = False
                self.calibrater.updateCalibration(
                    self.frame, self.poseRecover.homography)

        # convert to required format for streaming
        if ret:
            ret, jpeg = cv2.imencode('.jpg', self.frame)
            return jpeg.tobytes()

        else:
            return None

    def get_frame_calib(self, start_calib):
        ret, self.frame = self.cap.read()
        self.calibFrame = np.copy(self.frame)


        if(start_calib):
            if(not self.calibrater.calibrationDone):
                if (self.calibrater.aruco_ids is None):
                    self.calibrater.noOfFrames = 0
                    self.calibrater.prevArucoCorners = []
                    textsize = cv2.getTextSize("MARKER NOT FOUND!", cv2.FONT_HERSHEY_PLAIN, 3, 4)[0]
                    cv2.putText(self.frame, "MARKER NOT FOUND!", (int((self.frame.shape[1] - textsize[0]) / 2), int((self.frame.shape[0] + textsize[1]) / 2)), cv2.FONT_HERSHEY_PLAIN, 3,
                                (0, 0, 255), 4)
                else:
                    if (len(self.calibrater.aruco_ids) == 0):
                        self.calibrater.noOfFrames = 0
                        self.calibrater.prevArucoCorners = []
                        textsize = cv2.getTextSize("MARKER NOT FOUND!", cv2.FONT_HERSHEY_PLAIN, 3, 4)[0]
                        cv2.putText(self.frame, "MARKER NOT FOUND!", (int((self.frame.shape[1] - textsize[0]) / 2), int((self.frame.shape[0] + textsize[1]) / 2)), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)
                    else:
                        if(not self.calibrater.arucoFixed):
                            textsize = cv2.getTextSize("MARKER POSITION NOT FIXED", cv2.FONT_HERSHEY_PLAIN, 2, 3)[0]
                            cv2.putText(self.frame, "MARKER POSITION NOT FIXED", (int((self.frame.shape[1] - textsize[0]) / 2), int((self.frame.shape[0] + textsize[1]) / 2)), cv2.FONT_HERSHEY_PLAIN, 2,
                                        (0, 0, 255), 3)
                        else:
                            textsize = cv2.getTextSize("WAIT CALIBRATING", cv2.FONT_HERSHEY_PLAIN, 3, 4)[0]
                            cv2.putText(self.frame, "WAIT CALIBRATING", (int((self.frame.shape[1] - textsize[0]) / 2), int((self.frame.shape[0] + textsize[1]) / 2)), cv2.FONT_HERSHEY_PLAIN, 3,
                                        (0, 255, 255), 4)
            else:
                textsize = cv2.getTextSize("CALIBRATION COMPLETE", cv2.FONT_HERSHEY_PLAIN, 3, 4)[0]
                cv2.putText(self.frame, "CALIBRATION COMPLETE", (int((self.frame.shape[1] - textsize[0]) / 2), int((self.frame.shape[0] + textsize[1]) / 2)), cv2.FONT_HERSHEY_PLAIN, 3,
                            (0, 255, 0), 4)

        # convert to required format for streaming
        if ret:
            ret, jpeg = cv2.imencode('.jpg', self.frame)
            return jpeg.tobytes()

        else:
            return None
