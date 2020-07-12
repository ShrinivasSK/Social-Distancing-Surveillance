from flask import Flask, render_template, Response, jsonify, request
from camera import VideoCamera
import cv2
import yaml
import socket
import io
from _thread import *
import threading

app = Flask(__name__)
video_camera = None
global_frame = None
is_auto = False
calib_now = False
marker_length = 7.2
calib_start = False

gui_index_on = False
gui_calib_on = False


@app.route('/')
# Main page Rendering
def index():
    """Video streaming"""
    return render_template('index.html')


@app.route('/calibrate-screen')
# Calibration Page Rendering
def calibrate():
    """Video streaming"""
    return render_template('calibrate.html')


@app.route('/credits-screen')
# Main page Rendering
def credits():
    """Video streaming"""
    return render_template('credits.html')


def video_stream():
    # basic function to use the VideoCamera object in camera.py
    # to get a frame in req format and stream it
    global video_camera
    global global_frame

    if video_camera == None:
        video_camera = VideoCamera()

    video_camera.calibrater.checkIntrinstics()
    video_camera.calibrater.checkCalibration()

    while True:
        # returns frame in required format
        frame = video_camera.get_frame()

        # frame streaming part
        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')


def video_stream_calib():
    # basic function to use the VideoCamera object in camera.py
    # to get a frame in req format and stream it
    global video_camera
    global global_frame
    global calib_start

    if video_camera == None:
        video_camera = VideoCamera()

    video_camera.calibrater.calibrationDone = 0
    calib_start = False

    while True:
        # returns frame in required format
        frame = video_camera.get_frame_calib(calib_start)

        # frame streaming part
        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')


@app.route('/video_feed')
# This is the video streaming Route. Used in src attribute of image tag in HTML
# To stream the video
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_calib')
# This is the video streaming Route. Used in src attribute of image tag in HTML
# To stream the video
def video_feed_calib():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(video_stream_calib(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/min-dist', methods=['POST'])
def get_min_dist():
    json = request.get_json()
    video_camera.min_dist = float(json['min-dist'])*100
    with open('min_dist.txt', 'w') as file:
        file.write(str(video_camera.min_dist))
    return jsonify(result="done")


@app.route('/start_stop_index', methods=['POST'])
def onstart_stop_index():
    json = request.get_json()
    print(json['action'])
    global gui_index_on
    global gui_calib_on
    if(json['action'] == 'start'):
        gui_index_on = True
        gui_calib_on = False
        print(gui_index_on)
        try:
            with open('loginDetails.yaml') as f:
                loadedData = yaml.safe_load(f)
            username = loadedData.get('username')
            password = loadedData.get('password')
            data = {
                "username": str(username),
                "password": str(password),
                "thresh": str(video_camera.min_dist),
            }
            return jsonify(data)
        except:
            print("Couldn't open login yaml file")
            return jsonify(result="error")

    else:
        gui_index_on = False
        return jsonify(result="done")


@app.route('/start_stop_calib', methods=['POST'])
def onstart_stop_calib():
    json = request.get_json()
    print(json['action'])
    global gui_calib_on
    global gui_index_on
    if (json['action'] == 'start'):
        gui_calib_on = True
        gui_index_on = False
        try:
            with open('calibrationData.yaml') as f:
                loadedData = yaml.safe_load(f)
            aruco_length = loadedData.get('aruco_length')
            data = {
                "markerDimension": str(aruco_length),
            }
            return jsonify(data)
        except:
            print("Couldn't open login yaml file")
            return jsonify(result="error")
    else:
        gui_calib_on = False
        return jsonify(result="done")


@ app.route('/recalib', methods=['POST'])
# Handle recalibration calls
def recalib():
    json = request.get_json()
    action = json['action']

    # if auto calibration is on
    if(action == "auto-calib"):
        # Check whether camera is initalised
        # Will be unless fatal error
        if(video_camera == None):
            return jsonify(result="error")
        video_camera.is_auto = True
        return jsonify(result="done")
    # if auto calibration is off
    elif(action == "manual-calib"):
        if(video_camera == None):
            return jsonify(result="error")
        video_camera.is_auto = False
        return jsonify(result="done")
    # if calibrate now button is pressed
    elif(action == "calib-now"):
        print(video_camera.calibNow)
        if(video_camera == None):
            return jsonify(result="error")
        # If Recalibration is going on
        if(video_camera.calibNow):
            return jsonify(result="Already On")
        # If background is not calculated yet
        if(not video_camera.poseRecover.backgroundFound):
            return jsonify(result="Finding Background")
        video_camera.calibNow = True
        return jsonify(result="done")


@ app.route('/marker-dimension', methods=['POST'])
# Get the data about marker dimensions and store in global variable
def getDimension():
    global marker_length
    json = request.get_json()
    marker_length = float(json['side-length'])
    return jsonify(result="done")


@ app.route('/calib-start', methods=['POST'])
# Handle Calibration start calls from Calibration page
def startCalib():
    global calib_start
    if(video_camera == None):
        return jsonify(result="Error")
    calib_start = True
    # Loop runs a code in Camera.py till the calibration is done
    # and then sends the data back to the HTML page
    while not video_camera.calibrater.calibrationDone:
        video_camera.getCalibData(marker_length, calib_start)
    return jsonify(video_camera.calibrater.calibData)


@ app.route('/save-changes', methods=['POST'])
# When user confirms the data output from calibration
def save_changes():
    json = request.get_json()

    # Save it in yaml file
    with open(r'data.yaml', 'w') as file:
        yaml.dump(json, file)
    return jsonify(result="normal")


def nonGUICode():
    global video_camera
    if(not (video_camera is None)):
        if(video_camera.calibrater.calibrationDone):
            video_camera.is_auto = True
            video_camera.get_frame()
            if(video_camera.social_distancing_violated):
                print("Social Distancing Violated!")
        else:
            global calib_start
            # calib_start = True
            video_camera.get_frame_calib(True)
            video_camera.getCalibData(marker_length, True)
    else:
        video_camera = VideoCamera()


def runNonGUI():
    while True:
        # print("INDEX")
        # print(gui_index_on)
        # print("CALIB")
        # print(gui_calib_on)
        if ((not gui_index_on) and (not gui_calib_on)):
            nonGUICode()


# main server starting
if __name__ == '__main__':
    start_new_thread(runNonGUI, ())
    app.run(host='0.0.0.0', debug=False, threaded=True, use_reloader=False)
