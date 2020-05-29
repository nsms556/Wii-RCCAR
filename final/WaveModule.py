import Jetson.GPIO as GPIO
from time import sleep, time

WAVE_MAX_DISTANCE = 300
WAVE_MAX_DURATION = (WAVE_MAX_DISTANCE * 2 * 29.1)
WAVE_DIS_MINIMUM = 10

WAVE_TRIG = 24
WAVE_ECHO = 26

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(WAVE_TRIG, GPIO.OUT)
GPIO.setup(WAVE_ECHO, GPIO.IN)

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
        sleep(0.01)
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
        sleep(0.01)
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
        sleep(0.01)
        pulse_duration = (pulse_end - pulse_start)* 1000000
        dis = distanceCM(pulse_duration)
        dis = round(dis, 2)
    else :
        dis = -1
    
    return dis
