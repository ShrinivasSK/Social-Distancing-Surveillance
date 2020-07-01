from flask import Flask, render_template, Response, jsonify, request
from camera import VideoCamera
import cv2
import yaml
import socket
import io
import threading

app = Flask(__name__)
video_camera = None
global_frame = None
is_auto = False
calib_now = False
marker_length = 7.2
calib_start = False


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


def video_stream():
    # basic function to use the VideoCamera object in camera.py
    # to get a frame in req format and stream it
    global video_camera
    global global_frame

    if video_camera == None:
        video_camera = VideoCamera()

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


@app.route('/video_feed')
# This is the video streaming Route. Used in src attribute of image tag in HTML
# To stream the video
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/min-dist', methods=['POST'])
def min_dist():
    json = request.get_json()
    min_dist = json['min-dist']
    with open('min_dist.txt', 'w') as file:
        file.write(min_dist)
    return jsonify(result="done")


@app.route('/recalib', methods=['POST'])
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


@app.route('/marker-dimension', methods=['POST'])
# Get the data about marker dimensions and store in global variable
def getDimension():
    global marker_length
    json = request.get_json()
    marker_length = float(json['side-length'])
    return jsonify(result="done")


@app.route('/calib-start', methods=['POST'])
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


@app.route('/save-changes', methods=['POST'])
# When user confirms the data output from calibration
def save_changes():
    json = request.get_json()

    # Save it in yaml file
    with open(r'data.yaml', 'w') as file:
        yaml.dump(json, file)
    return jsonify(result="normal")


# main server starting
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, threaded=True, use_reloader=False)
