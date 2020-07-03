import numpy as np
import cv2
import yaml
from cv2 import aruco
from math import sqrt

aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
# ARUCO Board used for finding Intrinstics
aruco_board = aruco.GridBoard_create(5, 7, 2.3, 0.5, aruco_dict)


class CameraCalibration:

    def __init__(self):
        self.cameraMatrix = None
        self.distCoeffs = None
        self.repError = 0.0
        self.intrinsticDone = 0
        self.aruco_rvecs = []
        self.aruco_tvecs = []
        self.aruco_ids = []
        self.aruco_corners = [[]]
        self.allCornersConcatenated_Intrinstic = [[]]
        self.allIdsConcatenated_Intrinstic = []
        self.markerCounterPerFrame_Intrinstic = []
        self.rvecs_Intrinstic = []
        self.tvecs_Intrinstic = []
        self.arucoLength = 0.0  # in cm
        self.worldRatio = 0.0  # in cm^2
        self.topViewTransform = None
        self.calibrationDone = 0
        self.calibData = {}
        self.noOfFrames = 0
        self.prevArucoCorners = []
        self.arucoFixed = 1

        self.checkIntrinstics()
        self.checkCalibration()

    def checkIntrinstics(self):
        try:
            with open('intrinsicsData.yaml') as f:
                loadedData = yaml.safe_load(f)
            self.cameraMatrix = loadedData.get('camera_matrix')
            self.distCoeffs = loadedData.get('dist_coeff')
            self.cameraMatrix = np.array(self.cameraMatrix)
            self.distCoeffs = np.array(self.distCoeffs)
            self.intrinsticDone = 1
        except:
            print("Error opening intrinsicsData.yaml")
            self.intrinsticDone = 0

    def checkCalibration(self):
        try:
            with open('calibrationData.yaml') as f:
                loadedData = yaml.load(f)
            self.aruco_corners = loadedData.get('aruco_corners')
            self.aruco_ids = loadedData.get('aruco_ids')
            self.aruco_rvecs = loadedData.get('aruco_rvecs')
            self.aruco_tvecs = loadedData.get('aruco_tvecs')
            self.arucoLength = loadedData.get('aruco_length')
            self.topViewTransform = loadedData.get('topViewTransform')
            self.worldRatio = loadedData.get('worldRatio')

            self.aruco_corners = np.array(self.aruco_corners)
            self.aruco_ids = np.array(self.aruco_ids)
            self.aruco_rvecs = np.array(self.aruco_rvecs)
            self.aruco_tvecs = np.array(self.aruco_tvecs)
            self.topViewTransform = np.array(self.topViewTransform)
            self.calibrationDone = 1
        except:
            print("Error opening calibrationData.yaml")
            self.calibrationDone = 0

    def detectMarkers(self, img):
        corners, ids, _ = cv2.aruco.detectMarkers(img, aruco_dict)
        return (corners, ids)

    def findIntrinstics(self, img):
        if len(self.markerCounterPerFrame_Intrinstic) >= 15:
            self.markerCounterPerFrame_Intrinstic = np.array(
                self.markerCounterPerFrame_Intrinstic)

            self.repError, mtx, distC, self.rvecs_Intrinstic, self.tvecs_Intrinstic = cv2.aruco.calibrateCameraAruco(
                self.allCornersConcatenated_Intrinstic, self.allIdsConcatenated_Intrinstic,
                self.markerCounterPerFrame_Intrinstic, aruco_board, (img.shape[0], img.shape[1]), None, None)

            self.intrinsticDone = 1
            self.cameraMatrix = mtx
            self.distCoeffs = distC

            data = {'camera_matrix': np.asarray(self.cameraMatrix).tolist(
            ), 'dist_coeff': np.asarray(self.distCoeffs).tolist()}
            try:
                with open("intrinsicsData.yaml", "w") as f:
                    yaml.dump(data, f)
            except:
                print("ERROR creating intrinsicsData.yaml file")
                exit(0)
        else:
            corners, ids = self.detectMarkers(img)
            if(not(ids is None)):
                if(len(ids) > 0):
                    if (len(self.markerCounterPerFrame_Intrinstic) == 0):
                        self.allCornersConcatenated_Intrinstic = corners
                        self.allIdsConcatenated_Intrinstic = ids
                    else:
                        self.allCornersConcatenated_Intrinstic = np.vstack(
                            (self.allCornersConcatenated_Intrinstic, corners))
                        self.allIdsConcatenated_Intrinstic = np.vstack(
                            (self.allIdsConcatenated_Intrinstic, ids))
                    self.markerCounterPerFrame_Intrinstic.append(len(ids))

    def reFindIntrinstics(self, img):
        self.allCornersConcatenated_Intrinstic.clear()
        self.allIdsConcatenated_Intrinstic.clear()
        self.markerCounterPerFrame_Intrinstic.clear()
        self.intrinsticDone = 0

    def undistortInput(self, img):
        if(self.cameraMatrix is None or self.distCoeffs is None):
            print("Intrinstic parameters not found")
            return None
        else:
            frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            frame = cv2.undistort(frame, self.cameraMatrix, self.distCoeffs)
            return frame

    def findTopViewTransform(self, img):
        sum_arr = []
        for i in range(0, 4):
            sum_arr.append(
                int(self.aruco_corners[0][0][i][0] + self.aruco_corners[0][0][i][1]))

        top_left_index = 0
        min_val = img.shape[0] + img.shape[1]

        for i, val in enumerate(sum_arr):
            if val < min_val:
                min_val = val
                top_left_index = i

        top_right_index = (
            top_left_index + 1) if ((top_left_index + 1) < 4) else (top_left_index + 1 - 4)
        bottom_right_index = (
            top_left_index + 2) if ((top_left_index + 2) < 4) else (top_left_index + 2 - 4)
        bottom_left_index = (
            top_left_index + 3) if ((top_left_index + 3) < 4) else (top_left_index + 3 - 4)

        pts_src = []
        pts_src.extend([self.aruco_corners[0][0][top_left_index], self.aruco_corners[0][0][top_right_index],
                        self.aruco_corners[0][0][bottom_right_index], self.aruco_corners[0][0][bottom_left_index]])

        pts_dst = [(450, 550), (500, 550), (500, 600), (450, 600)]

        pts_src = np.array(pts_src)
        pts_dst = np.array(pts_dst)
        trform, _ = cv2.findHomography(pts_src, pts_dst)
        self.topViewTransform = trform

    def findTopView(self, img):
        if(self.topViewTransform is None):
            return None
        else:
            size = (1000, 1000)
            topView = np.zeros(size, dtype='uint8')
            topView = cv2.warpPerspective(img, self.topViewTransform, size)
            return topView

    def findWorldRatio(self, topView):
        corners, ids = self.detectMarkers(topView)
        if(not(ids is None)):
            if(len(ids) > 0):
                arucoArea = (0.5) * (((corners[0][0][0][0] * corners[0][0][1][1])
                                      + (corners[0][0][1][0]
                                         * corners[0][0][2][1])
                                      + (corners[0][0][2][0]
                                         * corners[0][0][3][1])
                                      + (corners[0][0][3][0] * corners[0][0][0][1]))
                                     - ((corners[0][0][1][0] * corners[0][0][0][1])
                                        + (corners[0][0][2][0]
                                           * corners[0][0][1][1])
                                        + (corners[0][0][3][0]
                                           * corners[0][0][2][1])
                                        + (corners[0][0][0][0] * corners[0][0][3][1])))

                self.worldRatio = (self.arucoLength ** 2) / arucoArea
                self.worldRatio = sqrt(self.worldRatio)

    def reCalibrate(self, img, arucoLength):
        self.aruco_corners.clear()
        self.aruco_ids.clear()
        self.aruco_rvecs.clear()
        self.aruco_tvecs.clear()
        self.worldRatio = 0.0
        self.calibrate(img, arucoLength)

    def updateCalibration(self, img, newRMat, newTvec):
        cameraMatrixInverse = np.linalg.inv(self.cameraMatrix)
        rvecMat = newRMat

        newTransform = np.zeros((4, 4))
        for i in range(0, 3):
            for j in range(0, 3):
                newTransform[i][j] = rvecMat[i][j]
        newTransform[3][3] = 1
        newTransform[0][3] = newTvec[0][0]
        newTransform[1][3] = newTvec[1][0]
        newTransform[2][3] = newTvec[2][0]

        for i in range(0, 4):
            arucoCorner = np.zeros((3, 1))
            arucoCorner[0][0] = self.aruco_corners[0][0][i][0]
            arucoCorner[1][0] = self.aruco_corners[0][0][i][1]
            arucoCorner[2][0] = 1

            arucoCorner = cameraMatrixInverse.dot(arucoCorner)
            arucoCornerInCFrame = np.zeros((4, 1))
            arucoCornerInCFrame[0][0] = arucoCorner[0][0]
            arucoCornerInCFrame[1][0] = arucoCorner[1][0]
            arucoCornerInCFrame[2][0] = arucoCorner[2][0]
            arucoCornerInCFrame[3][0] = 1

            newArucoCornerInCFrame = newTransform.dot(arucoCornerInCFrame)

            temp = np.array(([1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]))
            newArucoCorner = temp.dot(newArucoCornerInCFrame)
            newArucoCorner = self.cameraMatrix.dot(newArucoCorner)
            self.aruco_corners[0][0][i][0] = newArucoCorner[0][0]
            self.aruco_corners[0][0][i][1] = newArucoCorner[1][0]

        self.aruco_rvecs, self.aruco_tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(self.aruco_corners, 0.05,
                                                                                    self.cameraMatrix,
                                                                                    self.distCoeffs)
        self.findTopViewTransform(img)
        arucoCornersInTopView = []
        for i in range(0, 4):
            temp = np.zeros((3, 1))
            temp[0][0] = self.aruco_corners[0][0][i][0]
            temp[1][0] = self.aruco_corners[0][0][i][1]
            temp[2][0] = 1

            cornerInTopView = self.topViewTransform.dot(temp)
            print(cornerInTopView)
            corner = np.zeros((1, 2))
            corner[0][0] = cornerInTopView[0][0]
            corner[0][1] = cornerInTopView[1][0]
            arucoCornersInTopView.append(corner)

        arucoCornersInTopView = np.array(arucoCornersInTopView)

        arucoArea = (0.5) * (((arucoCornersInTopView[0][0][0] * arucoCornersInTopView[1][0][1])
                              + (arucoCornersInTopView[1][0][0]
                                 * arucoCornersInTopView[2][0][1])
                              + (arucoCornersInTopView[2][0][0]
                                 * arucoCornersInTopView[3][0][1])
                              + (arucoCornersInTopView[3][0][0] * arucoCornersInTopView[0][0][1]))
                             - ((arucoCornersInTopView[1][0][0] * arucoCornersInTopView[0][0][1])
                                + (arucoCornersInTopView[2][0][0]
                                   * arucoCornersInTopView[1][0][1])
                                + (arucoCornersInTopView[3][0][0]
                                   * arucoCornersInTopView[2][0][1])
                                + (arucoCornersInTopView[0][0][0] * arucoCornersInTopView[3][0][1])))

        self.worldRatio = (self.arucoLength ** 2) / arucoArea
        self.worldRatio = sqrt(self.worldRatio)

        rvecMat = np.zeros((3, 3))
        cv2.Rodrigues(self.aruco_rvecs[0], rvecMat)
        cameraPosition = -np.matrix(rvecMat).transpose() * \
            np.matrix(self.aruco_tvecs[0]).transpose()

        ##########################################################################
        # find camera Pose and save in yaml file
        self.calibData = {'height': str(np.asarray(np.abs(cameraPosition[2]) * 100).tolist()[0][0]),
                          'distance': str(np.asarray(np.abs(cameraPosition[1]) * 100).tolist()[0][0]),
                          'yaw': str(np.asarray((self.aruco_rvecs[0][0][2] * 180) / np.pi).tolist()),
                          'pitch': str(np.asarray((self.aruco_rvecs[0][0][1] * 180) / np.pi).tolist()),
                          'roll': str(np.asarray((self.aruco_rvecs[0][0][0] * 180) / np.pi).tolist())}

        calibrationData = {
            'aruco_corners': np.asarray(self.aruco_corners).tolist(),
            'aruco_ids': np.asarray(self.aruco_ids).tolist(),
            'aruco_rvecs': np.asarray(self.aruco_rvecs).tolist(),
            'aruco_tvecs': np.asarray(self.aruco_tvecs).tolist(),
            'aruco_length': self.arucoLength,
            'worldRatio': self.worldRatio,
            'topViewTransform': np.asarray(self.topViewTransform).tolist()
        }

        try:
            with open("calibrationData.yaml", "w") as f:
                yaml.dump(calibrationData, f)
        except:
            print("ERROR creating calibrationData.yaml file")
            return 0
        ##########################################################################

        if (self.worldRatio == 0):
            return 0
        return 1

    def calibration(self, img):
        self.aruco_rvecs, self.aruco_tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(self.aruco_corners, 0.05,
                                                                                    self.cameraMatrix,
                                                                                    self.distCoeffs)
        self.findTopViewTransform(img)
        topView = self.findTopView(img)
        self.findWorldRatio(topView)

        rvecMat = np.zeros((3, 3))
        cv2.Rodrigues(self.aruco_rvecs[0], rvecMat)
        cameraPosition = -np.matrix(rvecMat).transpose() * \
            np.matrix(self.aruco_tvecs[0]).transpose()

        ##########################################################################
        # find camera Pose and send it to HTML page
        self.calibData = {'height': str(np.asarray(np.abs(cameraPosition[2]) * 100).tolist()[0][0]),
                          'distance': str(np.asarray(np.abs(cameraPosition[1]) * 100).tolist()[0][0]),
                          'yaw': str(np.asarray((self.aruco_rvecs[0][0][2] * 180) / np.pi).tolist()),
                          'pitch': str(np.asarray((self.aruco_rvecs[0][0][1] * 180) / np.pi).tolist()),
                          'roll': str(np.asarray((self.aruco_rvecs[0][0][0] * 180) / np.pi).tolist())}

        ##########################################################################

        calibrationData = {
            'aruco_corners': np.asarray(self.aruco_corners).tolist(),
            'aruco_ids': np.asarray(self.aruco_ids).tolist(),
            'aruco_rvecs': np.asarray(self.aruco_rvecs).tolist(),
            'aruco_tvecs': np.asarray(self.aruco_tvecs).tolist(),
            'aruco_length': self.arucoLength,
            'worldRatio': self.worldRatio,
            'topViewTransform': np.asarray(self.topViewTransform).tolist()
        }

        try:
            with open("calibrationData.yaml", "w") as f:
                yaml.dump(calibrationData, f)
        except:
            print("ERROR creating calibrationData.yaml file")
            return 0

        if (self.worldRatio != 0):
            self.calibrationDone = 1
        else:
            self.calibrationDone = 0
            return 0
        return 1

    def calibrate(self, img, arucoLength):
        self.arucoLength = arucoLength
        self.aruco_corners, self.aruco_ids = self.detectMarkers(img)
        if(not(self.aruco_ids is None)):
            if(len(self.aruco_ids) > 0):

                if(self.noOfFrames == 0):
                    self.prevArucoCorners = []
                    self.prevArucoCorners.append(self.aruco_corners[0][0][0])
                    self.prevArucoCorners.append(self.aruco_corners[0][0][1])
                    self.prevArucoCorners.append(self.aruco_corners[0][0][2])
                    self.prevArucoCorners.append(self.aruco_corners[0][0][3])
                    self.prevArucoCorners = np.array(self.prevArucoCorners)
                else:
                    currentArucoCorners = []
                    currentArucoCorners.append(self.aruco_corners[0][0][0])
                    currentArucoCorners.append(self.aruco_corners[0][0][1])
                    currentArucoCorners.append(self.aruco_corners[0][0][2])
                    currentArucoCorners.append(self.aruco_corners[0][0][3])
                    currentArucoCorners = np.array(currentArucoCorners)

                    diffInPosition = currentArucoCorners - self.prevArucoCorners
                    #print(diffInPosition)

                    is_stable_1 = np.all((diffInPosition <= 2))
                    is_stable_2 = np.all((diffInPosition >= -2))
                    if(not (is_stable_1 and is_stable_2)):
                        self.noOfFrames = 0
                        self.arucoFixed = 0
                    else:
                        self.arucoFixed = 1

                    if(self.noOfFrames >= 15):
                        self.arucoFixed = 1
                        if(self.calibration(img)):
                            return 1
                        else:
                            return 0

                self.noOfFrames = self.noOfFrames + 1
            else:
                self.calibrationDone = 0
                print("ARUCO NOT DETECTED!")
                return 0
        else:
            self.calibrationDone = 0
            print("ARUCO NOT DETECTED!")
            return 0


######################################################
''' For Testing
cap = cv2.VideoCapture(0)

if cap.isOpened() == True:
    exit

calibrater = CameraCalibration()
cv2.namedWindow("Input", cv2.WINDOW_NORMAL)
cv2.namedWindow("Alternate_topView", cv2.WINDOW_NORMAL)

while True:
    _, frame = cap.read()
    if(calibrater.intrinsticDone):
        img = calibrater.undistortInput(frame)
        if(not(img is None)):
            if(calibrater.calibrationDone):
                # print("WORLD RATIO = {:.2f}".format(calibrater.worldRatio))
                topView = calibrater.findTopView(frame)
                if(not(topView is None)):
                    cv2.imshow("Alternate_topView", topView)
                else:
                    print("Error in finding top view")
            else:
                calibrater.calibrate(frame, 7.2)
        else:
            print("Intrinstics not found")
    else:
        calibrater.findIntrinstics(frame)

    cv2.imshow("Input", frame)
    cv2.waitKey(1)
'''
