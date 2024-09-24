from datetime import datetime

class Classification:

    def __init__(self, category):
        self.category = category
        self.category_index = 6
        self.timestamp = datetime.now()
        self.confidence = 0
        self.votes = [0, 0, 0, 0, 0, 0, 0]

    def update(self, confidence, categories, category_index):
        self.votes[category_index] += 1
        most_voted = 0
        for i in range(len(self.votes)):
            if self.votes[i] > self.votes[most_voted]:
                most_voted = i
        self.category = categories[most_voted]
        if category_index == most_voted:
            if confidence > self.confidence:
                self.confidence = confidence
        self.category_index = most_voted
        self.timestamp = datetime.now()

    def to_string(self):
        # return (self.category.description).upper() + ' (' + str(round(self.classification_confidence * 100)) + ')'
        return (self.category.description).upper() + ' - ' + str(round(self.confidence*100,2)) + '%'
