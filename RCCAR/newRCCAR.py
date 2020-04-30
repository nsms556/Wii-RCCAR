import cwiid as c
from time import sleep
from RCStatic import *
import RPi.GPIO as GPIO

def initWiimote() :
    global wii
    
    print("Press Wiimote 1 + 2 Button to Connection")
    sleep(1)

    try :
        wii = c.Wiimote()
    except RuntimeError :
        print("Wiimote Failed")
        quit()

    wii.rpt_mode = c.RPT_BTN | c.RPT_ACC
    
    print("Quit to Press Buttons + and -")
    sleep(3)

def initRC() :
    global servo, dcMotor

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(MOTOR_DIR, GPIO.OUT)
    GPIO.setup(MOTOR_PWM, GPIO.OUT)	
    GPIO.setup(SERVO, GPIO.OUT)
    GPIO.setup(HEADLIGHT, GPIO.OUT)
	
    servo = GPIO.PWM(SERVO, 50)
    dcMotor = GPIO.PWM(MOTOR_PWM, 100)
	
    servo.start(0)
    dcMotor.start(0)

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

def servoTest() :
    global servo

    servo.ChangeDutyCycle(5)
    sleep(1)
    
    servo.ChangeDutyCycle(10)
    sleep(1)
	
    servo.ChangeDutyCycle(8)
    sleep(1)

def setLight(light) :
    global wii
    buttons = wii.state['buttons']

    if( buttons & c.BTN_DOWN ) :
        if(light == LED_ON) :
            retLight = LED_OFF
        else :
            retLight = LED_ON
    else :
        retLight = light

    return retLight

def setShift():
    global wii
    buttons = wii.state["buttons"]

    if(buttons & c.BTN_2 and buttons & c.BTN_1):
        shift = SHIFT_STOP
    elif((buttons & c.BTN_2) == 0 and (buttons & c.BTN_1) == 0):
        shift = SHIFT_STOP
    elif(buttons & c.BTN_2):
        shift = SHIFT_FORWARD
    elif(buttons & c.BTN_1):
        shift = SHIFT_BACKWARD

    return shift

def setSteer():
    global wii
    steerVal = wii.state["acc"][1]

    if(steerVal >= STEER_LEFTLIMIT):
        steer = STEER_LEFTLIMIT
    elif(steerVal <= STEER_RIGHTLIMIT):
        steer = STEER_RIGHTLIMIT
    else:
        steer = steerVal

    return steer

def setQuit() :
    global wii
    buttons = wii.state["buttons"]

    if(buttons & c.BTN_PLUS and buttons & c.BTN_MINUS) :
        isQuit = 1
    else :
        isQuit = 0

    return isQuit

def wii_quit() :
    global wii

    print("Wiimote Power Off")
    wii.rumble = 1
    sleep(1)
    wii.rumble = 0
    exit(wii)

def setHeadLight(status) :
    if(status == LED_ON) :
        GPIO.output(HEADLIGHT, True)
    else :
        GPIO.output(HEADLIGHT, False)

def setMotorForward() :
    GPIO.output(MOTOR_DIR, True)

def setMotorBackward() :
    GPIO.output(MOTOR_DIR, False)

def setMotorSpeed(speedValue) :
    dcMotor.ChangeDutyCycle(speedValue)

def setServoSteer(steer) :
    servo.ChangeDutyCycle(valConvert(steer))

def RCCon() :

    speed = 0
    headlight = LED_OFF

    while True :
        shift = setShift()
        steer = setSteer()
        isQuit = setQuit()
        headlight = setLight(headlight)
		
        if(isQuit == 1) :
            wii_quit()
            break

        if(shift == SHIFT_FORWARD) :
            setMotorForward()
            if(speed + 0.2 <= SPEED_LIMIT) :
                speed += 0.2
            setMotorSpeed(speed)
        elif(shift == SHIFT_BACKWARD) :
            setMotorBackward()
            if(speed + 0.2 <= SPEED_LIMIT) :
                speed += 0.2
            setMotorSpeed(speed)
        else :
            if(speed - 1.5 < 0) :
                speed = 0
            else :
                speed -= 1.5
            setMotorSpeed(speed)

        setServoSteer(steer)
        
        setHeadLight(headlight)

        sleep(BUTTON_DELAY)

def main(self) :

    initRC()
    initWiimote()

    servoTest()
    
    RCCon()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
