import cv2, atexit
from datetime import datetime

camera_port = 3

cap = cv2.VideoCapture(camera_port)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
frame = []
ret = []
firstFrame = None
isRunning = None
def camRun():
    try:
        if isRunning == False: btnStop()
        ret, frame = cap.read()
        # cv2.putText(frame, "Front", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        # cv2.putText(frame, datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        if ret or frame.any(): return autoAdjustments_with_convertScaleAbs(frame)
    except: return None

def autoAdjustments_with_convertScaleAbs(img):
    alow = img.min()
    ahigh = img.max()
    amax = 255
    amin = 0
    alpha = ((amax - amin) / (ahigh - alow))
    beta = amin - alow * alpha
    new_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    return new_img

def exit_handler(): btnStop()

def btnStop(): cap.release(); cv2.destroyAllWindows()

def start_cam(): isRunning = True; atexit.register(exit_handler)
