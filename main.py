#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for, Response, request, send_from_directory
from camera import VideoCamera
import Adafruit_PCA9685
import smbus
import math
import time
import sys
import os

#-------#
# SERVO #
#-------#

servos = [1.7,1.3]			# [obrot, pochylenie]
delta = 0.05
pwm = Adafruit_PCA9685.PCA9685()
servoMax = [2.8,1.9]			# [max obrot, max pochylenie]
servoMin = [0.7,0.7]			# [min obrot, min pochylenie]
rotate = -1

def set_servo_pulse(channel, pulse):
	global pwm
	pulse_length = 1000000		# 1,000,000 (us/s)
	pulse_length //= 60		# 60 Hz
	pulse_length //= 4096		# 12 bitow rozdzielczosci
	pulse *= 1000
	pulse //= pulse_length
	pwm.set_pwm(channel, 0, int(pulse))

#-------#
# FLASK #
#-------#

app = Flask(__name__)
app.config['DEBUG'] = True

# @app.route('/')
# def index(): 
# 	return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid credentials. Please try again.'
        else:
        	return render_template('index.html')
            # return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
	global servos, delta, rotate
	if string == 'up':
		servos[1] -= delta
	if string == 'down':
		servos[1] += delta
	if string == 'left':
		servos[0] += delta
	if string == 'right':
		servos[0] -= delta
	if string == 'center':
		servos = [1.7,1.3]
	
	for i in range (0, 2):
		if servos[i] > servoMax[i]:
			servos[i] = servoMin[i]
		if servos[i] < servoMin[i]:
			servos[i] = servoMax[i]
		set_servo_pulse(i, servos[i])
		print servos[i]

	return 'Ok'

if __name__ == '__main__':
	pwm.set_pwm_freq(60)
	app.run(host='0.0.0.0', port=5000, debug=True, passthrough_errors=False, threaded=True)
