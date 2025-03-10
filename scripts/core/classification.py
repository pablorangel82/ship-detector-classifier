from datetime import datetime
from core.category import Category

class Classification:

    def __init__(self):
        self.timestamp = datetime.now()
        self.categories=[]
        self.elected = None
        for i in range(len(Category.CATEGORIES)):
            confidence_list = [None for element in range(10)]
            self.categories.append((Category.CATEGORIES[i], 0, 0, None))

    def update(self, confidence, category_index, bbox):
        category = Category.CATEGORIES[category_index]
        votes = self.categories [category_index] [1]
        votes+=1
        self.categories [category_index] = (category, votes, confidence, bbox)
        if self.elected is None or votes > self.elected[1]:
            self.elected = self.categories [category_index]
        self.timestamp = datetime.now()
            
    def to_string(self):
        return (self.elected[0].name).upper() + ' - ' + str(round(self.elected[2]*100,2)) + '%'
