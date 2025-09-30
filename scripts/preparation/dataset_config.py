import os

class DatasetConfig:
    SRC_LINK = "https://www.shipspotting.com/photos/"
    ENI_LIST = "preparation/resources/eni.dat"
    SRC_FOLDER = os.path.join ("D:\\","src_download")
    ORIGINAL_DATASET_FOLDER = os.path.join ("D:\\","dataset","first_schema")
    AUGMENTED_DATASET_FOLDER = os.path.join ("D:\\","dataset","first_schema_augumented_V1")
    TRAIN_PERC = 0.70
    TEST_PERC = 0.15
    target_img_width = 640
    target_img_height = 640