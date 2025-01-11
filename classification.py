from datetime import datetime
from category import Category

class Classification:

    def __init__(self):
        self.category = Category.CATEGORIES[len(Category.CATEGORIES) - 1]
        self.timestamp = datetime.now()
        self.confidence = 0
        self.votes=[]
        for cat in Category.CATEGORIES:
            self.votes.append(0)

    def update(self, confidence, category_index):
        self.votes[category_index] += 1
        most_voted = max(range(len(self.votes)),key=self.votes.__getitem__)
        self.category = Category.CATEGORIES[most_voted]
        if category_index == most_voted:
            self.confidence = confidence
        self.timestamp = datetime.now()

    def to_string(self):
        return (self.category.description).upper() + ' - ' + str(round(self.confidence*100,2)) + '%'
