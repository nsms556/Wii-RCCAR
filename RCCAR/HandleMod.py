import cwiid as c
from time import sleep
from RCStatic import *
    
class Handle :
    
    def __init__(self) :
        self.shift = SHIFT_STOP
        self.steer = STEER_NOLRDIR
        self.horn = HORN_OFF
        self.isQuit = 0
        
        print("Press Wiimote 1 + 2 Buttons to Connection")
        sleep(1)
        
        try :
            self.wii = c.Wiimote()
        except RuntimeError :
            print("Failed to Connect Wiimote")
            quit()
        
        print("Quit to Press Buttons + and -")
        sleep(2)
        
        self.wii.rpt_mode = c.RPT_BTN | c.RPT_ACC
    
    def wii_quit(self) :
        global wii
        print("Wiimote Power Off")
        self.wii.rumble = 1
        sleep(1)
        self.wii.rumble = 0
        exit(self.wii)

    def setShift(self) :
        buttons = self.wii.state["buttons"]

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
        steerVal = self.wii.state["acc"][1]
        
        if(steerVal >= STEER_LEFTLIMIT) :
            steer = STEER_LEFTLIMIT
        elif(steerVal <= STEER_RIGHTLIMIT) :
            steer = STEER_RIGHTLIMIT
        else :
            steer = steerVal
        
        return steer
    
    def setHorn(self) :
        buttons = self.wii.state["buttons"]
        
        if(buttons & c.BTN_A) :
            horn = HORN_ON
        elif(buttons & c.BTN_1) :
            horn = SHIFT_BACKWARD
        else :
            horn = HORN_OFF

        return horn
    
    def setQuit(self) :
        buttons = self.wii.state["buttons"]
        
        if(buttons & c.BTN_PLUS and buttons & c.BTN_MINUS) :
            isQuit = 1
        else :
            isQuit = 0
            
        return isQuit
            
    def getHandleCon(self) :
        shift = self.setShift()
        steer = self.setSteer()
        horn = self.setHorn()
        isQuit = self.setQuit()
        return shift, steer, horn, isQuit

