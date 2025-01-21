from detection_management import DetectionManagement
from viewer import view
import cv2

detection_management = DetectionManagement('rstp_example', 'en')
detection_management.start()

while True:
    img_to_show,tracks_list = detection_management.detect_estimate_and_classify()
    if img_to_show is not None:
        view(img_to_show, tracks_list)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break