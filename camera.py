import cv2
import numpy as np
import threading
from RecoverPose import recoverPose
import datetime
from cameraCalib import CameraCalibration

global_frame = None


class VideoCamera(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame = self.cap.read()
        # initalise the functional objects
        self.poseRecover = recoverPose(np.identity(3))
        self.calibrater = CameraCalibration()

        # when calibrate now button is clicked this variable changes
        self.calibNow = False
        # when the auto recalibration toggle is changed then this variable changes
        self.is_auto = False
        # to calibrate after every hour
        self.startingTime = datetime.datetime.now()

    def __del__(self):
        self.cap.release()

    def getCalibData(self, aruco_length, start_calib):
        # To avoid re reading from camera which leads to lagging
        # we are saving the frame as a property
        frame = self.frame

        #code to run the calibration 
        #this is a block inside a while loop so is continuously running
        #till calibration is done
        if(start_calib):
            if(self.calibrater.intrinsticDone):
                img = self.calibrater.undistortInput(frame)
                if(not(img is None)):
                    if(self.calibrater.calibrationDone):
                        #print("WORLD RATIO = {:.2f}".format(self.calibrater.worldRatio))
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

        # check whether we have to start calibration now
        # starts every hour if is_auto is true and the background has been detected
        # and the calibration is not on currently (if someone uses manual calibration)
        if(self.is_auto and datetime.datetime.now().hour-self.startingTime.hour == 1 and self.poseRecover.backgroundFound and not self.calibNow):
            print("auto calib start")
            self.startingTime = datetime.datetime.now()
            self.calibNow = True
            self.poseRecover.calibrated = False

        #till the bcakground is not found this part runs
        if(not self.poseRecover.backgroundFound):
            self.poseRecover.original_background(self.frame)
        else:
            #if calibrate Now button is clicked this runs
            if(self.calibNow and not self.poseRecover.calibrated):
                self.poseRecover.pose(self.frame)
            if(self.calibNow and self.poseRecover.calibrated):
                #when recalibration is done
                self.calibNow = False
                self.poseRecover.calibrated = False
                self.calibrater.updateCalibration(
                    self.frame, self.poseRecover.R_mat, self.poseRecover.t_mat)

        # convert to required format for streaming
        if ret:
            ret, jpeg = cv2.imencode('.jpg', self.frame)
            return jpeg.tobytes()

        else:
            return None
