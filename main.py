#!/usr/bin/env python

from flask import Flask, render_template, Response, request, send_from_directory
from camera import VideoCamera
import thread
import smbus
import math
import time
import sys
import os

app = Flask(__name__)
app.config['DEBUG'] = True

servos = [0.0, 0.0]

def servoHandler(threadName, delay):
	while True:
		print "*"
		time.sleep(1)

@app.route('/')
def index(): 
	return render_template('index.html')

def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
	return Response(gen(VideoCamera()),
					mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control/<string>',methods=['GET','POST'])
def control(string):
	if string == 'up':
		return 'Ok'
	if string == 'down':
		return 'Ok'
	if string == 'left':
		return 'Ok'
	if string == 'right':
		return 'Ok'

if __name__ == '__main__':
	try:
		thread.start_new_thread(servoHandler, ("servoHandler", 0))
	except:
		print "Error: unable to start thread"
	app.run(host='0.0.0.0', port=5000, debug=True, passthrough_errors=False, threaded=True)