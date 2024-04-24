import uuid
import classification
import kinematic


class Track:
    NUMBER_OF_SAMPLES = 2
    uuid = ''
    name = None
    kinematic = None
    classification = None

    def __init__(self):
        self.uuid = 'UUID-EN-CAMERA-' + str(uuid.uuid4())
        self.kinematic = kinematic.Kinematic()
        self.classification = classification.Classification()

    def to_string(self):
        string = '\nId: ' + self.get_name() + '\n Classification: ' + self.classification.to_string() + '\n Kinematic: ' + self.kinematic.to_string()
        return string

    def get_name(self):
        name = self.name
        if name is None:
            name = self.uuid[len(self.uuid) - 3] + self.uuid[len(self.uuid) - 2] + self.uuid[len(self.uuid) - 1]
        return name
