from core.dcm import DCM
from core.viewer import view
import cv2


dcm = DCM('core/config/setup', 'en')
dcm.start()
dcm.camera.set_to_track_position(45,2500)
while True:
    img_to_show,tracks_list = dcm.detect_estimate_and_classify()
    if img_to_show is not None:
        view(img_to_show, tracks_list, dcm.camera)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break