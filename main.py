import time
from detection_management import DetectionManagement
import stream_server
from datetime import datetime
from viewer import view
import cv2
FORCED_DELAY = 0 #seconds

detection_management = DetectionManagement('rstp_example', 'ptbr')
detection_management.start()
#stream_server.run()

while True:
    img_to_show,tracks_list = detection_management.detect_estimate_and_classify()
    if img_to_show is not None:
        #stream_server.generate(img_to_show, tracks_list)
        view(img_to_show, tracks_list)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break