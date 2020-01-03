import cwiid as c
from time import sleep
from RCStatic import *
    
class Handle :
    shift = SHIFT_STOP
    steer = STEER_NOLRDIR
    horn = HORN_OFF
    
    def __init__(self) :
        global wii, buttons
        print("Press Wiimote 1 + 2 Buttons to Connection")
        sleep(1)
        
        try :
            wii = c.Wiimote()
        except RuntimeError :
            print("Failed to Connect Wiimote")
            quit()
        
        print("Quit to Press Buttons + and -")
        sleep(2)
        
        wii.rpt_mode = c.RPT_BTN | c.RPT_ACC

    def wii_quit(self) :
        global wii

        printf("Wiimote Power Off")
        wii.rumble = 1
        time.sleep(1)
        wii.rumble = 0
        exit(wii)
    
    def setShift(self) :
        global wii
        buttons = wii.state["buttons"]

        if(buttons & c.BTN_2 and buttons & c.BTN_1) :
            shift = SHIFT_STOP
        elif((buttons & c.BTN_2) == 0 and (buttons & c.BTN_1) == 0) :
            shift = SHIFT_STOP
        elif(buttons & c.BTN_2) :
            shift = SHIFT_FORWARD
        elif(buttons & c.BTN_1) :
            shift = SHIFT_BACKWARD

        return shift
    
    def setSteer(self) :
        global wii
        steerVal = wii.state["acc"][1]
        
        if(steerVal >= STEER_LEFTLIMIT) :
            steer = STEER_LEFTLIMIT
        elif(steerVal <= STEER_RIGHTLIMIT) :
            steer = STEER_RIGHTLIMIT
        else :
            steer = steerVal
        
        return steer
    
    def setHorn(self) :
        global wii
        buttons = wii.state["buttons"]
        
        if((buttons & c.BTN_A) == 0) :
            horn = HORN_OFF
        elif(buttons & c.BTN_A) :
            horn = HORN_ON

        return horn
        
    def getHandleCon(self) :
        global shift, steer, horn
        
        shift = self.setShift()
        steer = self.setSteer()
        horn = self.setHorn()

        return shift, steer, horn
