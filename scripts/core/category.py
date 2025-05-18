import importlib

class Category():
    CATEGORIES = {}

    def __init__(self, id, name, max_air_draught, min_air_draught, avg_air_draught, source_key):
        self.id = id
        self.name = name
        self.max_air_draught = max_air_draught
        self.min_air_draught = min_air_draught
        self.avg_air_draught = avg_air_draught
        self.source_key = source_key
   
    @staticmethod
    def load_categories(language):
        module_name = "categories.category_"+language
        module = importlib.import_module(module_name)
        categories_list = getattr(module, "categories", None)
        for json_obj in categories_list:
            cat = categories_list [json_obj]
            category = Category(cat['id'], cat['name'], cat['max_air_draught'], cat['min_air_draught'], cat['avg_air_draught'], str(json_obj))
            Category.CATEGORIES[category.id] = category
        return Category.CATEGORIES