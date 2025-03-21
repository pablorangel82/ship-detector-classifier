import time
import json
import threading
from onvif import ONVIFCamera

import api.config.logging_config as logger

class ONVIFControl():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path):
        if self._initialized:
            return
        
        json_file = open(config_path + '.json')
        self.config_data = json.load(json_file)
        self.onvif_data = self.config_data['onvif']
        self.cam_connection = None
        self.ptz_service = None
        self.token = None
        self.pan = None
        self.tilt = None
        self.zoom = None

    def connect(self):
        connected = False
        while not connected:
            try:
                self.cam_connection = ONVIFCamera(
                    self.onvif_data['ip'],
                    self.onvif_data['port'], 
                    self.onvif_data['username'],
                    self.onvif_data['password']
                )
                self.ptz_service = self.cam_connection.create_ptz_service()

                media_service = self.cam_connection.create_media_service()
                self.token = media_service.GetProfiles()[0].token

                connected = True
                logger.log.info(f'PTZ obtido com sucesso')
            except Exception as error:
                logger.log.error(f'Impossível obter PTZ da câmera: {error}')
                time.sleep(5)  # espera 5 segundos antes de tentar novamente

    def move_right(self, distance=0.01):
        pan, tilt, zoom = self.get_ptz_status()
        pan = pan + distance
        self.perform_move(pan, tilt)

    def move_left(self, distance=0.01):
        pan, tilt, zoom = self.get_ptz_status()
        pan = pan - distance
        self.perform_move(pan, tilt)

    def move_up(self, distance=0.02):
        pan, tilt, zoom = self.get_ptz_status()
        tilt = tilt + distance
        self.perform_move(pan, tilt)

    def move_down(self, distance=0.02):
        pan, tilt, zoom = self.get_ptz_status()
        tilt = tilt - distance
        self.perform_move(pan, tilt)

    def zoom_out(self, distance=0.05):
        pan, tilt, zoom = self.get_ptz_status()
        zoom = zoom - distance

        self.perform_zoom(zoom)

    def zoom_in(self, distance=0.05):
        pan, tilt, zoom = self.get_ptz_status()
        zoom = zoom + distance

        self.perform_zoom(zoom)

    def center(self):
        self.perform_move(0, 0)
        self.perform_zoom(0)

    def perform_move(self, pan, tilt):
        request = self.ptz_service.create_type('AbsoluteMove')
        request.ProfileToken = self.token

        if pan > 1:
            pan = 1
        elif pan < -1:
            pan = -1

        if tilt > 1:
            tilt = 1
        elif tilt < -1:
            tilt = -1

        request.Position = {
            'PanTilt': {'x': pan, 'y': tilt}
        }

        self.ptz_service.AbsoluteMove(request)

    def perform_zoom(self, zoom):
        request = self.ptz_service.create_type('AbsoluteMove')
        request.ProfileToken = self.token

        if zoom > 1:
            zoom = 1
        elif zoom < 0:
            zoom = 0

        request.Position = {
            'Zoom': {'x': zoom}
        }

        self.ptz_service.AbsoluteMove(request)

    def set_ptz_status(self):
        while True:
            if self.cam_connection and self.token:
                status = self.ptz_service.GetStatus({'ProfileToken': self.token})
                self.pan = status.Position.PanTilt.x
                self.tilt = status.Position.PanTilt.y
                self.zoom = status.Position.Zoom.x

    def get_ptz_status(self):
        return self.pan, self.tilt, self.zoom
    
    def start_status_after_connect(self):
        self.connect()
        threading.Thread(target=self.set_ptz_status, daemon=True).start()  
