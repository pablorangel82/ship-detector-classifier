import os

class DatasetConfig:
    SRC_LINK = "https://www.shipspotting.com/photos/"
    ENI_LIST = "../../scripts/resources/eni.dat"
    SRC_FOLDER = os.path.join ("D:\\","src_download")
    DATASET_FOLDER = os.path.join ("D:\\","dataset")
    TRAIN_PERC = 0.80
    TEST_PERC = 0
    target_img_width = 640
    target_img_height = 640