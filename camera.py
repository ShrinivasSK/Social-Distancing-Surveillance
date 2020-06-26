import cv2
import threading

# for the recording part 
class RecordingThread (threading.Thread):
    def __init__(self, name, camera):
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True

        self.cap = camera
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter(
            './static/video.avi', fourcc, 20.0, (640, 480))

    def run(self):
        while self.isRunning:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)

        self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()


class VideoCamera(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

        # Initialize video recording environment
        self.is_record = False
        self.out = None

        # Thread for recording
        self.recordingThread = None

    def __del__(self):
        self.cap.release()
    
    #here we can run the Pose Calibration function and it will return the output
    def getPoseData(self):
        ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #dummy output
        PoseData = {'length': str(frame[0, 0]), 'width': str(frame[1, 1]), 'height': str(frame[2, 2]),
                    'distance': str(frame[3, 3]), 'yoke': str(frame[4, 4]), 'pitch': str(frame[5, 5]), 'roll': str(frame[6, 6])}
        return PoseData

    #here we will run the camera callibraion part and it can save the callib data in a file
    #not showing the camera paramters in the UI
    def getCamData(self):
        ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #basic function to get the frame in the required format for streaming
    def get_frame(self, action):
        ret, frame = self.cap.read()

        #if we implement top view then we can use this to change the frame top view
        if(action == "Top_View"):
            #dummy function on the frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #convert to required format
        if ret:
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()

        else:
            return None

    def start_record(self):
        self.is_record = True
        self.recordingThread = RecordingThread(
            "Video Recording Thread", self.cap)
        self.recordingThread.start()

    def stop_record(self):
        self.is_record = False

        if self.recordingThread != None:
            self.recordingThread.stop()


