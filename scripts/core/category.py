import importlib

class Category():
    CATEGORIES = {}

    def __init__(self, id, name, avg_air_draught, source_key):
        self.id = id
        self.name = name
        self.avg_air_draught = avg_air_draught
        self.source_key = source_key
   
    @staticmethod
    def load_categories(version, language):
        module_name = "categories.category_"+version+"_"+language
        module = importlib.import_module(module_name)
        categories_list = getattr(module, "categories", None)
        for json_obj in categories_list:
            cat = categories_list [json_obj]
            category = Category(cat['id'], cat['name'], cat['avg_air_draught'], str(json_obj))
            Category.CATEGORIES[category.id] = category
        return Category.CATEGORIES