from detection_management import DetectionManagement
from viewer import Viewer

detector_model = 'detector/detector.pb'
detector_config = 'detector/detector.pbtxt'
classifier_model = 'classifier/model.pb'
# sample = 'barca'
sample = None
detection_management = DetectionManagement(detector_model,detector_config,classifier_model,'en', 'ptbr', sample)
detection_management.start()
viewer = Viewer()

while True:
    img_to_show,tracks_list = detection_management.detect_estimate_and_classify()
    if img_to_show is not None:
        viewer.show_image(img_to_show, tracks_list, detection_management.control_access_track_list)
    if viewer.quit_command():
        break

viewer.exit()