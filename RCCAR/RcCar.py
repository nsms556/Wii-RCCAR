from HandleMod import Handle
from time import sleep
import RCStatic
import RPi.GPIO as GPIO
import os

def servoTest() :
	global servo
	
	servo.ChangeDutyCycle(5)
	sleep(1)

	servo.ChangeDutyCycle(10)
	sleep(1)
	
	servo.ChangeDutyCycle(8)
	sleep(1)

def valConvert(inVal) :
	if(inVal >= 117 and inVal <= 123) :
		val = 8
	else :
		val = round((float(200 - inVal) / 10), 1)
		if(val <= 5) :
			val = 5
		elif(val >= 10.5) :
			val = 10.5
	
	return val

def setMotorForward(speed) :
	GPIO.output(RCStatic.MOTOR_DIR, True)
	dcMotor.ChangeDutyCycle(speed)

def setMotorBackward(speed) :
	GPIO.output(RCStatic.MOTOR_DIR, False)
	dcMotor.ChangeDutyCycle(speed)

def setMotorStop(speed) :
	dcMotor.ChangeDutyCycle(speed)

def setServoSteer(steer) :
	servo.ChangeDutyCycle(valConvert(steer))
	
def init() :
	global servo, dcMotor, HandleCon, speed
	
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)

	GPIO.setup(RCStatic.MOTOR_DIR, GPIO.OUT)
	GPIO.setup(RCStatic.MOTOR_PWM, GPIO.OUT)	
	GPIO.setup(RCStatic.SERVO, GPIO.OUT)
	
	servo = GPIO.PWM(RCStatic.SERVO, 50)
	dcMotor = GPIO.PWM(RCStatic.MOTOR_PWM, 100)
	
	servo.start(0)
	dcMotor.start(0)
	
	speed = 0
	
	HandleCon = Handle()
	servoTest()

def mainControl():
	global dcMotor, servo, speed
	
	while True :
		shift, steer, horn, isQuit = HandleCon.getHandleCon()
		
		if(isQuit == 1) :
			HandleCon.wii_quit()
			break
			
		if(shift == 1) :
			setMotorForward(speed)
			if(speed + 0.2 <= 80) :
				speed += 0.2
		elif(shift == -1) :
			setMotorBackward(speed)
			if(speed + 0.2 <= 80) :
				speed += 0.2
		else :
			speed -= 1.5
			if(speed <=0) :
				speed = 0
			setMotorStop(speed)
			
		setServoSteer(steer)
	
		sleep(RCStatic.BUTTON_DELAY)

def systemOff() :
	os.system("sudo reboot now")

def main(self):
	init()
	
	mainControl()
	
	#systemOff()
	
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
