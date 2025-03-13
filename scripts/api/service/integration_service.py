import requests
import threading
import json
import time

import api.config.logging_config as logger
from api.service.tracking_service import TrackingService

class IntegrationService:
    def __init__(self, config_path, onvif_control, camera):
        json_file = open(config_path + '.json')
        self.config_data = json.load(json_file)
        self.camera_data = self.config_data['camera']
        self.rest_data = self.config_data['rest']
        self.onvif_control = onvif_control
        self.ptz_connection = False
        self.video_streaming_connection = False
        self.camera = camera
        threading.Thread(target=self.get_ptz, args=(f"{self.rest_data['ptz_url']}/{self.camera_data['ip']}", ), daemon=True).start()
        
    def get_ptz(self, url):
        headers = {
            'Authorization': f"Apikey {self.rest_data['apikey']}"
        }
        
        while self.ptz_connection is not True:
            try:
                response = requests.get(url, headers=headers, stream=True, verify=False)
                if response.status_code == 200:
                    self.ptz_connection = True
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8').strip()
                            if decoded_line.startswith("data: "):
                                event_data = decoded_line[5:].strip()
                            
                            command = json.loads(event_data)
                            match command:
                                case 'up':
                                    self.onvif_control.move_up()
                                case 'down':
                                    self.onvif_control.move_down()
                                case 'left':
                                    self.onvif_control.move_left()
                                case 'right':
                                    self.onvif_control.move_right()
                                case 'in':
                                    self.onvif_control.zoom_in()
                                case 'out':
                                    self.onvif_control.zoom_out()
                                case 'center':
                                    self.onvif_control.center()
                                case _:
                                    tracking_service = TrackingService(self.camera)
                                    tracking_service.track(command)
            
            except requests.exceptions.ChunkedEncodingError as e:
                logger.log.error(f'Requisição finalizada pelo servidor: {e}')
                self.ptz_connection = False
                
                
            except Exception as e:
                logger.log.error(f'Requisição finalizada pelo servidor: {e}')
                self.ptz_connection = False
                
            time.sleep(3)
            
    def video_stream(self, iterable):
        while not self.video_streaming_connection:
            try:
                headers = {
                    'Content-Type': 'text/event-stream',
                    'Authorization': f"Apikey {self.rest_data['apikey']}"
                }
                
                requests.post(
                    f"{self.rest_data['streaming_url']}/{self.camera_data['ip']}/{self.camera_data['id']}", 
                    headers=headers, 
                    data=iterable, 
                    verify=False
                )
                self.video_streaming_connection = True
            except requests.exceptions.ChunkedEncodingError as e:
                logger.log.error(f'Requisição finalizada pelo servidor: {e}')
                self.video_streaming_connection = False
                
            except Exception as e:
                logger.log.error(f'Requisição finalizada pelo servidor: {e}')
                self.video_streaming_connection = False
                
            time.sleep(3)