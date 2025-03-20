import cv2
import threading
import json

from core.dcm import DCM
from core.viewer import view
from api.service.integration_service import IntegrationService
from api.infrastructure.classification_publisher import ClassificationPublisher
from api.infrastructure.onvif_control import ONVIFControl
from core.camera import Camera

config_path = 'scripts/api/config/setup'

onvif_control = ONVIFControl(config_path)
threading.Thread(target=onvif_control.start_status_after_connect, daemon=True).start()

json_file = open(config_path+'.json')
config_data = json.load(json_file)
camera_data = config_data['camera']
camera = Camera(camera_data, onvif_control)

dcm = DCM(config_path, 'v1', 'ptbr', camera)
dcm.start()

classification_publisher = ClassificationPublisher()

integration_service = IntegrationService(config_path, onvif_control, camera)
threading.Thread(target=integration_service.video_stream, args=(classification_publisher, ), daemon=True).start()

while True:
    img_to_show,tracks_list = dcm.detect_estimate_and_classify()
    if img_to_show is not None:
        img_to_show = view(img_to_show, tracks_list, dcm.camera.bearing, [dcm.camera.pan,dcm.camera.tilt,dcm.camera.zoom])
        classification_publisher.write(img_to_show, tracks_list, onvif_control)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break