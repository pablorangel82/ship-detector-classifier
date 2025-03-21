class AcompanhamentoCameraDTO:
    def __init__(self, track):
        self.identificador = track.uuid.replace('EN-CAM-', '')
        self.fonte = 'EN'
        self.origem = 'CAM'
        self.nome = track.name
        self.velocidade = str(track.speed)
        self.rumo = str(track.course)
        self.latitude = str(track.lat)
        self.longitude = str(track.lon)
    
    def to_json(self):
        return {
            "identificador": self.identificador.upper(),
            "fonte": self.fonte,
            "origem": self.origem,
            "nome": self.nome,
            "velocidade": self.velocidade,
            # "sidc": self.sidc,
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