from preparation.automatic_labeling import label
from preparation.download import download
from preparation.show_samples import show
from preparation.dataset_statistics import collect
from core.category import Category
from preparation.distribute import distribute
from preparation.count import count
import logging
from preparation.dataset_config import DatasetConfig

logging.basicConfig(level=logging.INFO, format='%(message)s', )

categories = Category.load_categories('en')
if __name__ == '__main__':
    #download(start_again=True, auto_resize=False, all_categories = categories)
    #label(categories)
    #Should be considered the manual labeling process made. 
    #augmentation()
    #distribute()
    #collect(categories)
    count(DatasetConfig.ORIGINAL_DATASET_FOLDER)