import cwiid as c
from time import sleep
from RCStatic import *
import RCStatic
import RPi.GPIO as GPIO

def initWiimote(self) :
    print "Press Wiimote 1 + 2 Button to Connection"
    sleep(1)

    try :
        self.wii = c.Wiimote()
    except RuntimeError :
        print "Wiimote Failed"
        quit()

    self.wii.rpt_mode = c.RPT_BTN | c.RPT_ACC
    
    print "Quit to Press Buttons + and -"
    sleep(3)

def initRC(self) :
    global servo, dcMotor

    GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)

	GPIO.setup(RCStatic.MOTOR_DIR, GPIO.OUT)
	GPIO.setup(RCStatic.MOTOR_PWM, GPIO.OUT)	
	GPIO.setup(RCStatic.SERVO, GPIO.OUT)
	
	servo = GPIO.PWM(RCStatic.SERVO, 50)
	dcMotor = GPIO.PWM(RCStatic.MOTOR_PWM, 100)
	
	servo.start(0)
	dcMotor.start(0)

def servoTest() :
    global servo

    servo.ChangeDutyCycle(5)
	sleep(1)

	servo.ChangeDutyCycle(10)
	sleep(1)
	
	servo.ChangeDutyCycle(8)
	sleep(1)

def setShift(self):
    buttons = self.wii.state["buttons"]

    if(buttons & c.BTN_2 and buttons & c.BTN_1):
        shift = SHIFT_STOP
    elif((buttons & c.BTN_2) == 0 and (buttons & c.BTN_1) == 0):
        shift = SHIFT_STOP
    elif(buttons & c.BTN_2):
        shift = SHIFT_FORWARD
    elif(buttons & c.BTN_1):
        shift = SHIFT_BACKWARD

    return shift

def setSteer(self):
    steerVal = self.wii.state["acc"][1]

    if(steerVal >= STEER_LEFTLIMIT):
        steer = STEER_LEFTLIMIT
    elif(steerVal <= STEER_RIGHTLIMIT):
        steer = STEER_RIGHTLIMIT
    else:
        steer = steerVal

    return steer

def setHorn(self):
    buttons = self.wii.state["buttons"]

    if(buttons & c.BTN_A):
        horn = HORN_ON
    elif(buttons & c.BTN_1):
        horn = SHIFT_BACKWARD
    else:
        horn = HORN_OFF

    return horn

def setQuit(self) :
    buttons = self.wii.state["buttons"]

    if(buttons & c.BTN_PLUS and buttons & c.BTN_MINUS) :
        isQuit = 1
    else :
        isQuit = 0

    return isQuit

def wii_quit(self) :
    global wii

    print("Wiimote Power Off")
    self.wii.rumble = 1
    sleep(1)
    self.wii.rumble = 0
    exit(self.wii)

def setMotorForward() :
	GPIO.output(RCStatic.MOTOR_DIR, True)

def setMotorBackward(speed) :
	GPIO.output(RCStatic.MOTOR_DIR, False)

def setMotorSpeed(speedValue) :
    dcMotor.ChangeDutyCycle(speed)

def setMotorStop(speed) :
	dcMotor.ChangeDutyCycle(speed)

def setServoSteer(steer) :
	servo.ChangeDutyCycle(valConvert(steer))

def __init__(self) :

    initRC()
    initWiimote()

    servoTest()

def __main__(self) :

    speed = 0

    while True :
		shift = setShift()
        steer = setSteer()
        horn = setHorn()
        isQuit = setQuit()
		
		if(isQuit == 1) :
			wii_quit()
			break

        if(shift == SHIFT_STOP) :
            if(speed - 1.5 < 0) :
                speed = 0
            setMotorSpeed(speed)
		elif(shift == SHIFT_FORWARD) :
			setMotorForward(speed)
		elif(shift == SHIFT_BACKWARD) :
			setMotorBackward(speed)

        if(speed + 0.2 <= SPEED_LIMIT) :
			speed += 0.2
        
        setMotorSpeed(speed)
		setServoSteer(steer)
	
		sleep(RCStatic.BUTTON_DELAY)
