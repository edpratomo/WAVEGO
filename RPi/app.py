#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response, send_from_directory
from flask_cors import *
# import camera driver
#import camera_opencv
from camera_opencv import Camera
from camera_opencv import commandAct
import threading
import time

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)
CORS(app, supports_credentials=True)
camera = None

def get_camera():
    """Safely initialize the camera only once."""
    global camera
    if camera is None:
        print("[app.py] Initializing camera...")
        camera = Camera()
    return camera

def gen(camera_obj):
    """Video streaming generator function."""
    while True:
        #print(f"[DEBUG] Current Camera.modeSelect = {Camera.modeSelect}")
        frame = camera_obj.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.01)
        #yield (b'--frame\r\n'
        #       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    cam = get_camera()
    return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

dir_path = os.path.dirname(os.path.realpath(__file__))

@app.route('/api/img/<path:filename>')
def sendimg(filename):
    return send_from_directory(dir_path+'/dist/img', filename)

@app.route('/js/<path:filename>')
def sendjs(filename):
    return send_from_directory(dir_path+'/dist/js', filename)

@app.route('/css/<path:filename>')
def sendcss(filename):
    return send_from_directory(dir_path+'/dist/css', filename)

@app.route('/api/img/icon/<path:filename>')
def sendicon(filename):
    return send_from_directory(dir_path+'/dist/img/icon', filename)

@app.route('/fonts/<path:filename>')
def sendfonts(filename):
    return send_from_directory(dir_path+'/dist/fonts', filename)

@app.route('/<path:filename>')
def sendgen(filename):
    return send_from_directory(dir_path+'/dist', filename)

@app.route('/')
def index():
    return send_from_directory(dir_path+'/dist', 'index.html')

class webapp:
    #def __init__(self):
    #    self.camera = get_camera()

    def commandInput(self, inputCommand, valueA=None):
        #print(f"[DEBUG] inputCommand = {inputCommand}, valueA = {valueA}")
        commandAct(inputCommand, valueA)

    def modeselect(self, modeInput):
        cam = get_camera()
        cam.modeSelect = modeInput
        cam.CVMode = 'no'

    def colorFindSet(self, H, S, V):
        cam = get_camera()
        cam.colorFindSet(H, S, V)

    def thread(self):
        print("[app.py] Starting Flask server on port 5000...")
        app.run(host='0.0.0.0', port=5000 , threaded=True)
        print("[app.py] Flask server stopped.")

    def startthread(self):
        fps_threading=threading.Thread(target=self.thread)
        #fps_threading.setDaemon(False)
        fps_threading.start()

    def sendIP(self, ipInput):
        cam = get_camera()
        cam.upperIP(ipInput)
