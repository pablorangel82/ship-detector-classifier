import time
from detection_management import DetectionManagement
import stream_server

FORCED_DELAY = 0.03 #seconds

detection_management = DetectionManagement('rstp_example', 'ptbr')
detection_management.start()
stream_server.run()

while True:

    img_to_show,tracks_list = detection_management.detect_estimate_and_classify()

    if img_to_show is not None:
        stream_server.generate(img_to_show, tracks_list)
        if FORCED_DELAY > 0:
            time.sleep(FORCED_DELAY)