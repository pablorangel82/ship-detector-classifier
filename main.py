import time

import viewer
from detection_management import DetectionManagement
import stream_server

resolution = (1920,1080)
EMBEDDED_VIEWER = False
FORCED_DELAY = 0.02 #seconds

detector_model = 'detector/detector.pb'
detector_config = 'detector/detector.pbtxt'
classifier_model = 'classifier/classifier.pb'
detection_management = DetectionManagement(detector_model,detector_config,classifier_model,'rstp_example', 'ptbr')
detection_management.start()
viewer = viewer.Viewer(resolution)
stream_server.run()

while True:

    img_to_show,tracks_list = detection_management.detect_estimate_and_classify()

    if img_to_show is not None:
        if EMBEDDED_VIEWER:
            viewer.show_image(img_to_show,tracks_list)
            viewer.quit_command(detection_management.camera.frame_rate)
        else:
            stream_server.generate(img_to_show, tracks_list)
            if FORCED_DELAY > 0:
                time.sleep(FORCED_DELAY)