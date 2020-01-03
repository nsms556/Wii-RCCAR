from HandleMod import Handle
from time import sleep
import RCStatic
import RPi.GPIO as GPIO

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

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(RCStatic.MOTOR_DIR, GPIO.OUT)
GPIO.setup(RCStatic.MOTOR_PWM, GPIO.OUT)
GPIO.setup(RCStatic.SERVO, GPIO.OUT)
GPIO.setup(RCStatic.PIEZO, GPIO.OUT)

servo = GPIO.PWM(RCStatic.SERVO, 50)
dcMotor = GPIO.PWM(RCStatic.MOTOR_PWM, 100)

servo.start(0)
dcMotor.start(0)

HandleCon = Handle()

servo.ChangeDutyCycle(5)
sleep(1)

servo.ChangeDutyCycle(10)
sleep(1)

servo.ChangeDutyCycle(8)
sleep(1)

while True :
	shift, steer, horn = HandleCon.getHandleCon()
	
	if(shift == 1) :
		GPIO.output(RCStatic.MOTOR_DIR, True)
		dcMotor.ChangeDutyCycle(10)
	elif(shift == -1) :
		GPIO.output(RCStatic.MOTOR_DIR, False)
		dcMotor.ChangeDutyCycle(10)
	else :
		dcMotor.ChangeDutyCycle(0)
		
	servo.ChangeDutyCycle(valConvert(steer))
	
	sleep(RCStatic.BUTTON_DELAY)
