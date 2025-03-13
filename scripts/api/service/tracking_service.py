from core.track import Track

class TrackingService:
    def __init__(self, camera):
        self.camera = camera
        
    def track(self, goto):
        lat = goto.get('latitude')
        lon = goto.get('longitude')
        rumo = goto.get('rumo')
        velocidade = goto.get('velocidade')
        offset = goto.get('offset')
        
        track = Track(self.camera.id)
        track.lat = lat
        track.lon = lon
        track.course = rumo
        track.speed = velocidade
            
        print('\n')
        print(f"{track.lat}, {track.lon}")
        
        self.camera.tracking(track)