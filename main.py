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
action = None

#main page rendering
@app.route('/')
def index():
    """Video streaming"""
    return render_template('index.html')

#on calibrate button click this will render
@app.route('/calibrate-screen')
def calibrate():
    """Video streaming"""
    return render_template('calibrate.html')

#basic function to use the VideoCamera object in camera.py 
#to get a frame in req format and stream it
def video_stream():
    global video_camera
    global global_frame

    if video_camera == None:
        video_camera = VideoCamera()

    while True:
        frame = video_camera.get_frame(action)

        #frame streaming part
        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

#this is the src of the image tag in html
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#for the recording receive the HTTP request here
@app.route('/record_status', methods=['POST'])
def record_status():
    global video_camera
    if video_camera == None:
        video_camera = VideoCamera()

    json = request.get_json()
    status = json['status']
    if status == "true":
        video_camera.start_record()
        return jsonify(result="started")
    else:
        video_camera.stop_record()
        return jsonify(result="stopped")

#The main function part is this
#here we will get different POST requests for different actions
@app.route('/change-view', methods=['POST'])
def change_view():
    global video_camera
    global action

    json = request.get_json()
    action = json['action']
    #for the top view conversion on main page
    if(action == "Top_View"):
        return jsonify(result="done")
    
    #for coming back to camera view from top view
    elif(action == "Camera_View"):
        return jsonify(result="done")
    
    #for starting the pose calibration from calibration page
    elif(action == "Start_Pose"):
        if(video_camera == None):
            return jsonify(result="error")
        #here we are just sending the function output as a JSON to the html
        #where it shown in the form
        return jsonify(video_camera.getPoseData())
    
    #for camera calibration
    elif(action == "Start_Camera"):
        if(video_camera == None):
            return jsonify(result="error")
        #here just call the function written in camera.py
        video_camera.getCamData()
        return jsonify(result="Done")

#this is for the form in html page to be submitted
#we get all the form data here and we save it in a 
#yaml file
@app.route('/save-changes', methods=['POST'])
def save_changes():

    json = request.get_json()

    with open(r'data.yaml', 'w') as file:
        yaml.dump(json, file)

    return jsonify(result="normal")

#main server starting
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, threaded=True, use_reloader=False)
