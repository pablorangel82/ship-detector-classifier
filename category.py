import json

class Category():
    CATEGORIES = {}

    def __init__(self, id, description, avg_height):
        self.id = id
        self.description = description
        self.avg_height = avg_height

    @staticmethod
    def load_categories(language):
        json_file = open('classifier/category_' + language + '.json')
        config_data = json.load(json_file)
        for json_obj in config_data:
            cat = config_data [json_obj]
            category = Category(cat['id'], cat['name'], cat['avg_height'])
            Category.CATEGORIES[category.id] = category
        