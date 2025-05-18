from preparation.labeling import label
from preparation.download import download
from preparation.show_samples import show
from preparation.dataset_statistics import collect
from core.category import Category
from preparation.distribute import distribute
import logging
from preparation.versions import create_versions

logging.basicConfig(level=logging.INFO, format='%(message)s', )

categories = Category.load_categories('en')

create_versions()
#download(start_again=True, auto_resize=False, all_categories = categories)
#label(categories)
#show(categories)
#distribute()
#collect(categories)
