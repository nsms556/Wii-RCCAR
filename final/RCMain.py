import cwiid as c
from time import sleep, time
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
    GPIO.setup(BREAKLIGHT, GPIO.OUT)
    GPIO.setup(WAVE_TRIG, GPIO.OUT)
    GPIO.setup(WAVE_ECHO, GPIO.IN)
	
    servo = GPIO.PWM(SERVO, 50)
    dcMotor = GPIO.PWM(MOTOR_PWM, 100)
    
    servo.start(0)
    dcMotor.start(0)
    
    GPIO.output(WAVE_TRIG, False)
    
def distanceCM(duration) :
    return (duration / 2) / 29.1

def disMeasure() :
    dis = None
    pulse_start = None
    pulse_end = None
    GPIO.output(WAVE_TRIG, True)
    sleep(0.00001)
    GPIO.output(WAVE_TRIG, False)
    
    timeout = time()
    while GPIO.input(WAVE_ECHO) == 0 :
        pulse_start = time()
	if pulse_start != None :
	    if((pulse_start - timeout) * 1000000) >= WAVE_MAX_DURATION :
		dis = -1
		break
	else :
	    dis = -1
	    break
    
    if dis == -1 :
        return dis
    
    timeout = time()
    while GPIO.input(WAVE_ECHO) == 1 :
        pulse_end = time()
	if pulse_end != None :
	    if((pulse_end - pulse_start) * 1000000) >= WAVE_MAX_DURATION :
		dis = -1
		break
	else :
	    dis = -1
	    break
            
    if dis == -1 :
        return dis
    
    if pulse_start != None and pulse_end != None :
	pulse_duration = (pulse_end - pulse_start) * 1000000
	dis = distanceCM(pulse_duration)
	dis = round(dis, 2)
    else :
	dis = -1
    
    return dis
    
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

def setLight(light, lastLightTime) :
    global wii
    buttons = wii.state['buttons']
    
    if( buttons & c.BTN_DOWN ) :
	nowTime = time()
	if nowTime - lastLightTime > CONTROL_IGNORE :
	    newLight = light ^ True
	    newLightTime = time()
	else :
	    newLight = light
	    newLightTime = lastLightTime
    else :
	newLight = light
	newLightTime = lastLightTime

    return newLight, newLightTime

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

def setCruise(status, speed, shift, lastConTime) :
    global wii
    buttons = wii.state["buttons"]
    
    newStatus = CRUISE_OFF
    newConTime = 0
    
    if(buttons & c.BTN_UP) :
	nowTime = time()
	if nowTime - lastConTime > CONTROL_IGNORE :
	    if speed > CRUISE_MINIMUM :
		newStatus = status ^ True
		newConTime = time()
	else :
	    newStatus = status
	    newConTime = lastConTime
    elif (buttons & c.BTN_1) :
	newStatus = CRUISE_OFF
	newConTime = time()
    else :
	newStatus = status
	newConTime = lastConTime
	
    return newStatus, newConTime
	
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
    sleep(0.5)
    wii.rumble = 0
    exit(wii)

def setSpeed(speed, shift, cruise) :    
    newSpeed = 0
    
    if shift == SHIFT_FORWARD :
	if cruise == CRUISE_ON :
	    newSpeed = speed
	else :
	    if(speed + 0.2 <= SPEED_LIMIT) :
		newSpeed = speed + 0.2
	    else :
		newSpeed = speed
    elif shift == SHIFT_BACKWARD :
	if(speed + 0.2 <= SPEED_LIMIT) :
	    newSpeed = speed + 0.2
	else :
	    newSpeed = speed
    else :
	if(speed - 1 < 0) :
	    newSpeed = 0
	else :
	    newSpeed = speed - 1
		
    return newSpeed

def setHeadLight(status) :
    if(status == LED_ON) :
        GPIO.output(HEADLIGHT, True)
    else :
        GPIO.output(HEADLIGHT, False)

def setBreakLight(status) :
    if(status == LED_ON) :
        GPIO.output(BREAKLIGHT, True)
    else :
        GPIO.output(BREAKLIGHT, False)
	
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
    timeHL = time()
    timeCR = time()
    breaklight = LED_ON
    cruise = CRUISE_OFF
    backDistance = 0

    while True :
        shift = setShift()		    
        steer = setSteer()
        isQuit = setQuit()
        headlight, timeHL = setLight(headlight, timeHL)
	cruise, timeCR = setCruise(cruise, speed, shift, timeCR)
	backDistance = disMeasure()
		
        if(isQuit == 1) :
            setMotorSpeed(0)
            setServoSteer(120)
            setHeadLight(LED_OFF)
            setBreakLight(LED_OFF)
            wii_quit()
	    GPIO.cleanup()
            break
	
	if backDistance != None :
	    print('Back :', backDistance)
	    if backDistance < WAVE_DIS_MINIMUM and shift == SHIFT_BACKWARD :
		cruise = CRUISE_OFF
		shift = SHIFT_STOP
	
	if cruise == CRUISE_ON :
	    shift = SHIFT_FORWARD
	    
        if(shift == SHIFT_FORWARD) :
            setMotorForward()
            breaklight = LED_OFF
        elif(shift == SHIFT_BACKWARD) :
            setMotorBackward()
            breaklight = LED_ON
        else :
            breaklight = LED_ON
	    
	speed = setSpeed(speed, shift, cruise)
	print('Speed', round(speed,1))    
        setMotorSpeed(speed)
        setServoSteer(steer)
        setHeadLight(headlight)
        setBreakLight(breaklight)

        sleep(BUTTON_DELAY)

def main(self) :

    initRC()
    initWiimote()

    servoTest()
    
    RCCon()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
