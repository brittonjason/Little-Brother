#!/usr/bin/env python3

import sys
import time
import RPi.GPIO as GPIO




#Change the GPIO output for the LED light
#depending on the utilization percentage
#that the method is passed.
def changeLight(util_percent):
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(29, GPIO.OUT)
	GPIO.setup(31, GPIO.OUT)
	GPIO.setup(33, GPIO.OUT)
	#If less than 25%, light up GREEN
	if(util_percent < 0.25):
		GPIO.output(29, False)
		GPIO.output(31, True)
		GPIO.output(33, False)

	#If greater than 25% and less than 50%, light up YELLOW
	elif(util_percentage < 0.75):
		GPIO.output(29, True)
		GPIO.output(31, True)
		GPIO.output(33, False)

	#If greater than 75%, light up RED
	else:
		GPIO.output(29, False)
		GPIO.output(31, True)
		GPIO.output(33, False)


###Just for testing
p = 0.0
while(p < 1):
	changeLight(p)
	p = p+0.05
	time.sleep(1)


#Clean up when done
GPIO.cleanup()


