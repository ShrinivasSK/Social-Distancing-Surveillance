import numpy as np
import cv2

class recoverPose():

    def __init__(self, cameraMatrix):
        self.cameraMatrix = cameraMatrix
        self.k = 0
        self.frames = []
        self.background_curr = [[]]
        self.background_orig = [[]]
        self.calibrated = False
        self.backgroundFound = False
        self.R_mat = np.zeros((3, 3))
        self.t_mat = np.zeros((3, 1))
        self.homography = np.zeros((3, 3))

    def give_pose(self, img1, img2, cameraMatrix):
        R = np.zeros((3, 3))
        t = np.zeros((3, 1))

        orb = cv2.ORB_create()  # Feature matching using orb

        # Keypoints and descriptors in 1st image
        kp1, des1 = orb.detectAndCompute(img1, None)
        # keypoints and descriptors in 2nd image
        kp2, des2 = orb.detectAndCompute(img2, None)

        # Brute force matcher using NORM matching
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = matcher.match(des1, des2)
        # Sorting the matches according to distance
        matches = sorted(matches, key=lambda x: x.distance)
        good_matches = matches[:10]  # Taking the best 10 matches

        left_points = []
        right_points = []

        for m in good_matches:
            left_points.append(kp1[m.queryIdx].pt)
            right_points.append(kp2[m.trainIdx].pt)

        left_points = np.float32(left_points)
        right_points = np.float32(right_points)

        #cv2.drawKeypoints(img1, kp1, img1);
        #cv2.drawKeypoints(img2, kp2, img2);

        #To check feature matching
        #result = np.zeros((960, 1280))
        #result = cv2.drawMatches(img1, kp1, img2, kp2, good_matches, result);

        homography = np.zeros((3, 3))
        homography, _ = cv2.findHomography(left_points, right_points, cv2.RANSAC)

        ##To check feature matching by stitching images
        #homography_inv = np.zeros((3, 3))
        #homography_inv, _ = cv2.findHomography(right_points, left_points, cv2.RANSAC)
        #img2_changed = np.zeros((img1.shape[0] + img2.shape[0], img1.shape[1] + img2.shape[1]))
        #img2_changed = cv2.warpPerspective(img2, homography_inv, (img1.shape[0] + img2.shape[0], img1.shape[1] + img2.shape[1]))
        #for i in range(0, img1.shape[0]):
        #    for j in range(0, img1.shape[1]):
        #        img2_changed[i][j][0] = img1[i][j][0]
        #        img2_changed[i][j][1] = img1[i][j][1]
        #        img2_changed[i][j][2] = img1[i][j][2]

        #E, mask = cv2.findEssentialMat(
            #left_points, right_points, cameraMatrix, method=cv2.RANSAC, prob=0.999, threshold=1.0)

        #cv2.recoverPose(E, left_points, right_points, cameraMatrix, R, t, mask)

        return homography

    # Calcaulate the background
    def original_background(self, img):

        if self.k % 10 == 0:
            temp = img.copy()
            self.frames.append(temp)

        if len(self.frames) == 25:
            self.background_orig = np.median(
                self.frames, axis=0).astype(dtype=np.uint8)
            self.frames.clear()
            self.k = 0
            self.backgroundFound = True

        self.k = self.k+1

    # The Recalibration Code
    def pose(self, frame):

        if self.k % 10 == 0:
            temp = frame.copy()
            self.frames.append(temp)

        if len(self.frames) == 25:
            self.background_curr = np.median(
                self.frames, axis=0).astype(dtype=np.uint8)

            homography = self.give_pose(
                self.background_orig, self.background_curr, self.cameraMatrix)

            #self.R_mat = R
            #self.t_mat = t
            self.homography = homography
            self.calibrated = True

            self.frames.clear()
            self.k = 0

        self.k = self.k+1
