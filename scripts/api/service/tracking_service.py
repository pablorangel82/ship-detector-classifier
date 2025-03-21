from datetime import datetime, timezone
from core.track import Track
from core.kinematic import Kinematic
from core.converter import Converter

class TrackingService:
    def __init__(self, onvif_control, camera):
        self.camera = camera
        self.onvif_control = onvif_control
        
    def track(self, goto):
        lat = goto.get('latitude')
        lon = goto.get('longitude')
        rumo = goto.get('rumo', 0.0)
        velocidade = goto.get('velocidade', 0.0)
        offset = goto.get('offset')
        timestamp = datetime.strptime(goto.get('timestamp'), "%Y-%m-%dT%H:%M:%S.%f%z")#.replace(tzinfo=None)
        
        track = Track(self.camera.id)
        track.lat = lat
        track.lon = lon
        track.course = rumo
        track.speed = velocidade
        
        self.camera.timestamp_ptz = timestamp
        self.camera.tracking(track, offset)
        self.perform_move()
        
    def perform_move(self):
        self.onvif_control.perform_move(self.camera.pan, self.camera.tilt)
        self.onvif_control.perform_zoom(self.camera.zoom)