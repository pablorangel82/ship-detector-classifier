from datetime import datetime


class Classification:

    def __init__(self):
        self.category = ''
        self.category_index = 5
        self.timestamp = 0
        self.classification_confidence = 0
        self.detection_confidence = 0
        self.votes = [0, 0, 0, 0, 0, 0]

    def update(self, detection_confidence, classification_confidence, categories, category_index):
        self.votes[category_index] += 1
        most_voted = 0
        for i in range(len(self.votes)):
            if self.votes[i] > self.votes[most_voted]:
                most_voted = i
        self.category = categories[most_voted]
        self.detection_confidence = detection_confidence
        if category_index == most_voted:
            if classification_confidence > self.classification_confidence:
                self.classification_confidence = classification_confidence
        self.category_index = most_voted
        self.timestamp = datetime.now()

    def to_string(self):
        return (self.category.description).upper() + ' (' + str(round(self.classification_confidence * 100)) + ')'
