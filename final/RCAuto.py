import cv2
import LaneModule, ObjectModule

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

cam = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)

if cam.isOpened() :
    try :
        while True :
            ret, frame = cam.read()
            
            LaneModule.laneDeparture(frame)
            
            ObjectModule.findObject(frame)
            
            cv2.imshow('origin', frame)
            if cv2.waitKey(30) & 0xff == 27 :
                break
    finally :
        cv2.destroyAllWindows()
        cam.release()
else :
    print('NoVideo')
