from datetime import datetime

class Classification:

    def __init__(self, category):
        self.category = category
        self.timestamp = datetime.now()
        self.confidence = 0
        self.votes = [0, 0, 0, 0, 0, 0, 0]

    def update(self, confidence, categories, category_index):
        self.votes[category_index] += 1
        most_voted = max(range(len(self.votes)),key=self.votes.__getitem__)
        self.category = categories[most_voted]
        if category_index == most_voted:
            self.confidence = confidence
        self.timestamp = datetime.now()

    def to_string(self):
        return (self.category.description).upper() + ' - ' + str(round(self.confidence*100,2)) + '%'
