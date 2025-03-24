import cv2
import threading
import json

from core.dcm import DCM
from core.viewer import view
from api.service.integration_service import IntegrationService
from api.infrastructure.classification_publisher import ClassificationPublisher
from api.infrastructure.onvif_control import ONVIFControl
from api.infrastructure.service.rabbitMQ.sinal_acompanhamento_rabbitmq_service import SinalACompanhamentoCameraRabbitMQService
import api.config.logging_config as logger

api_config_path = 'scripts/api/config/api'
config_path = 'scripts/core/config/setup'

onvif_control = ONVIFControl(api_config_path)
threading.Thread(target=onvif_control.start_status_after_connect, daemon=True).start()

dcm = DCM(config_path, 'v1', 'ptbr')
dcm.start()
dcm.camera.set_to_track_position(45,2500)
while True:
    img_to_show,tracks_list = dcm.detect_estimate_and_classify()
    if img_to_show is not None:
        view(img_to_show, tracks_list, dcm.camera)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break