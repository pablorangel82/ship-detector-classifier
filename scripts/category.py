class Category():
    CATEGORIES = {}

    def __init__(self, id, description, avg_height):
        self.id = id
        self.description = description
        self.avg_height = avg_height

    @staticmethod
    def load_categories(language):
        category_file = __import__("category_"+language)
        for json_obj in category_file.categories:
            cat = category_file.categories [json_obj]
            category = Category(cat['id'], cat['name'], cat['avg_height'])
            Category.CATEGORIES[category.id] = category
        