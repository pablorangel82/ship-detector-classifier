from preparation.labeling import label
from preparation.download import download
from preparation.show_samples import show
from preparation.versions import create_versions
from preparation.dataset_statistics import collect
from core.category import Category
import logging


logging.basicConfig(level=logging.INFO, format='%(message)s', )

categories = Category.load_categories('v1','en')

download(start_again=True, auto_resize=False, all_categories = categories)
label(categories)
create_versions()
#show(categories)
collect(categories)