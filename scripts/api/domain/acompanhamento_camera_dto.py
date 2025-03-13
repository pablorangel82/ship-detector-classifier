import configparser

class AcompanhamentoCameraDTO:
    def __init__(self, track):
        self.config = configparser.ConfigParser()
        self.identificador = track.uuid.replace('EN-CAM-', '')
        self.fonte = 'EN'
        self.origem = 'CAM'
        self.nome = None
        self.velocidade = None
        self.rumo = None
        self.sidc = None
               
        lat, lon, speed, course, bbox = track.kinematic.get_current_kinematic()
        self.latitude = str(lat)
        self.longitude = str(lon)
        
        if track.name is not None:
            self.nome = str(track.name)

        if speed is not None:
            self.velocidade = str(speed)
            
        if course is not None:
            self.rumo = str(course)
    
    def to_json(self):
        return {
            "identificador": self.identificador.upper(),
            "fonte": self.fonte,
            "origem": self.origem,
            "nome": self.nome,
            "velocidade": self.velocidade,
            "sidc": self.sidc,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "rumo": self.rumo
        }
    
    def __str__(self):
        return f"""
            UUID: {self.identificador}
            Name: {self.nome}
            Latitude: {self.latitude}
            Longitude: {self.longitude}
            Velocidade: {self.velocidade}
            Rumo: {self.rumo}
        """