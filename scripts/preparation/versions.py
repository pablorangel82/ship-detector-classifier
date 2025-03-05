import os
import logging
import datetime
import shutil
import codecs
from core.category import Category
from preparation.dataset_config import DatasetConfig
import logging

v1_to_v2=[]
v1_to_v3=[]
v1 = None
v2 = None
v3 = None

def change_category(dir,dst_map):
    files = os.listdir(dir)
    for file in files:
        file_path = os.path.join(dir,file)
        tFile = codecs.open(file_path, 'r', 'utf-8')
        values = (tFile.read()).split()
        if len(values) == 0:
            continue
        tFile.close()
        tFile = codecs.open(file_path, 'w', 'utf-8')
        values[0] = get(int(values[0]),dst_map)
        line = str(values[0]) + ' ' + values[1] + ' ' + values[2] + ' ' + values[3] + ' ' + values[4]
        tFile.write(line)
        tFile.close()

def create_versions():
    create_maps()
    create_version('v2',v1_to_v2)
    create_version('v3',v1_to_v3)

def create_version(version, dst_map):
    logging.info("Version conversion started at " + str(datetime.datetime.now()))
    src_train_label_path = os.path.join(DatasetConfig.DATASET_FOLDER,"train","labels_v1")
    src_val_label_path = os.path.join(DatasetConfig.DATASET_FOLDER,"val","labels_v1")
    src_test_label_path = os.path.join(DatasetConfig.DATASET_FOLDER,"test","labels_v1")
    dst_train_label_path = os.path.join(DatasetConfig.DATASET_FOLDER,"train","labels_"+version)
    dst_val_label_path = os.path.join(DatasetConfig.DATASET_FOLDER,"val","labels_"+version)
    dst_test_label_path = os.path.join(DatasetConfig.DATASET_FOLDER,"test","labels_"+version)

    if os.path.exists(dst_train_label_path):
        shutil.rmtree(dst_train_label_path)
    shutil.copytree(src_train_label_path,dst_train_label_path)
    
    if os.path.exists(dst_test_label_path):
        shutil.rmtree(dst_test_label_path)
    shutil.copytree(src_test_label_path,dst_test_label_path)

    if os.path.exists(dst_val_label_path):
        shutil.rmtree(dst_val_label_path)
    shutil.copytree(src_val_label_path,dst_val_label_path)

    change_category(dst_train_label_path,dst_map)
    change_category(dst_val_label_path,dst_map)
    change_category(dst_test_label_path,dst_map)



def create_maps():
    global v1_to_v2,v1,v2
    v1 = Category.load_categories('v1','en')
    v2 = Category.load_categories('v2','en')
    v3 = Category.load_categories('v3','en')

    v1_to_v2.append([0,1,4,6,7,10,11,12,21,24])
    v1_to_v2.append([2,3])
    v1_to_v2.append([5,13,16,19,20,23,25])
    v1_to_v2.append([8,9])
    v1_to_v2.append([14,17])
    v1_to_v2.append([18])
    v1_to_v2.append([22])
    v1_to_v2.append([15])
    v1_to_v2.append([26])

    v1_to_v3.append([0,1,4,6,7,10,11,12,21,24])
    v1_to_v3.append([2,3,8,9])
    v1_to_v3.append([5,13,16,18,19,20,22,23,25])
    v1_to_v3.append([14,17])
    v1_to_v3.append([15])
    v1_to_v3.append([26])

    logging.info('\n *** V1 to V2 ***')
    print_map(v1_to_v2,v2)
    logging.info('\n *** V1 to V3 ***')
    print_map(v1_to_v3,v3)
    
def print_map(map, dst):
    for i in range(len(dst)):
        cat = dst[i]
        src_list = map[cat.id]
        logging.info('\n'+cat.name)
        for src_id in src_list:
            v1_cat = v1[src_id] 
            logging.info('\n\t'+v1_cat.name)

def get(id, map):
    for to_cat in map:
        if id in to_cat:
            return map.index(to_cat)
    return None