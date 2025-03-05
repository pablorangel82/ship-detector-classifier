from core.dcm import DCM
from core.viewer import view
import cv2


dcm = DCM('core/config/setup', 'v1', 'en')
dcm.start()

while True:
    img_to_show,tracks_list = dcm.detect_estimate_and_classify()
    if img_to_show is not None:
        view(img_to_show, tracks_list)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break