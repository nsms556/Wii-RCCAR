from adafruit_servokit import ServoKit
import cv2
import Lane

def gstreamer_pipeline(
    capture_width=640,
    capture_height=360,
    display_width=640,
    display_height=360,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def steerTranslate(value) :
    trans = int(value * 4 / 3 - 10)

    return trans

cam = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
kit = ServoKit(channels = 16)

if cam.isOpened() :
    try :
        while True :
            ret, frame = cam.read()
            steer = Lane.laneTracking(frame)
            if steer < 45 :
                steer = 45
            elif steer > 120 :
                steer = 120

            print('steer :', steer)
            kit.servo[0].angle = steerTranslate(steer)
            if cv2.waitKey(30) & 0xff == 27 :
                break
    finally :
        cv2.destroyAllWindows()
        cam.release()
else :
    print("NoVideo")
