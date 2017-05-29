#!flask/bin/python
from flask import Flask, jsonify, request, render_template
import RPi.GPIO as GPIO
import time
import os
import signal

app = Flask(__name__)

ControlPin = [11,15,38,40]

seq = [ [1,0,0,0],
	[1,1,0,0],
	[0,1,0,0],
	[0,1,1,0],
	[0,0,1,0],
	[0,0,1,1],
	[0,0,0,1],
	[1,0,0,1] ]

auto=0

def feed():
    global auto
    if(auto==0):
        GPIO.setmode(GPIO.BOARD)

    for pin in ControlPin:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,0)
        
    for i in range(64):
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(ControlPin[pin],seq[halfstep][pin])
            time.sleep(0.004)
                    
    if(auto==0):                
        GPIO.cleanup()

def startAutoFeed():
    global auto
    auto=1
    GPIO.setmode(GPIO.BOARD)
    TRIG = 16
    ECHO = 18
    currentTime = time.time() - 4*3600;
    
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)

    GPIO.output(TRIG, 0)

    while True:
        
        GPIO.output(TRIG, 0)                 #Set TRIG as LOW
        
        time.sleep(1)                            #Delay of 2 seconds

        GPIO.output(TRIG, 1)                  #Set TRIG as HIGH
        time.sleep(0.00001)                      #Delay of 0.00001 seconds
        GPIO.output(TRIG, 0)                 #Set TRIG as LOW

        while GPIO.input(ECHO)==0:               #Check whether the ECHO is LOW
            pulse_start = time.time()              #Saves the last known time of LOW pulse

        while GPIO.input(ECHO)==1 :               #Check whether the ECHO is HIGH
            pulse_end = time.time()                #Saves the last known time of HIGH pulse

        pulse_duration = pulse_end - pulse_start
        distance =pulse_duration * 17150
        distance = round(distance, 2)

        if time.time()-currentTime > 10  and distance > 2 and distance < 20:
            print 'Feeding Now!'
            feed()
            currentTime=time.time()
    GPIO.cleanup()
    auto=0

pid=0

@app.route('/')
def index():
    global pid
    print pid
    return render_template('index.html')

@app.route('/stop/')
def stop():
    global pid
    print pid
    if (pid > 0):
	os.kill(pid,signal.SIGKILL)
    return render_template('index.html')

@app.route('/feednow/')
def feedNow():
    print 'Feeding Now!'
    feed()
    return render_template('index.html')

@app.route('/autofeed/')
def autoFeed():
    global pid
    print 'Automatic feeding starting'
    pid  = os.fork()
    if (pid == 0):
        startAutoFeed()
    print pid
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')


    

