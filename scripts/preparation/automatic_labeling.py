from ultralytics import YOLO
import torch
import os
import cv2
import codecs
from preparation.dataset_config import DatasetConfig
import datetime
import logging
import threading
import time
import shutil

counter_train = []
counter_test = []
counter_val = []
counter_invalid = []
finish = []
categories = None
root_path = None

def show_status():
    global categories, counter_train, counter_test, counter_val, finish
    finished = False

    while finished == False:
        total_train = 0
        total_test = 0
        total_val = 0
        total_invalid = 0
        finished = True
        time.sleep(30)
        for cat in categories:
            index = int ((categories[cat])['id'])
            logging.info('\n\nCategory:' + cat)
            logging.info('Number of train files: ' + str(counter_train[index]))
            logging.info('Number of validation files: ' + str(counter_val[index]))
            logging.info('Number of test files: ' + str(counter_test[index]))
            logging.info('Number of files must be reviewed: ' + str(counter_invalid[index]))
            logging.info('Total: ' + str(counter_test[index]+counter_val[index]+counter_train[index]))

            total_train = counter_train [index] + total_train
            total_test = counter_test [index] + total_test
            total_val = counter_val [index] + total_val
            total_invalid = counter_invalid [index] + total_invalid

            finished = finish[index] and finished
            logging.info('Finished? ' + str(finish[index]))
 
        logging.info('\n\nResume: ')
        logging.info('Total files: ' + str(total_val+total_test+total_train))
        logging.info('Total train files: ' + str(total_train))
        logging.info('Total validation files: ' + str(total_val))
        logging.info('Total test files: ' + str(total_test))  
        logging.info('Total files to be reviewed: ' + str(total_invalid))

    lines = ''
    for cat in categories:
        index = int ((categories[cat])['id'])
        name = (categories[cat])['name']
        lines += str(index) + ',' + name + ', ' + str(counter_train[index]) + ', ' + str(counter_val[index]) + ', ' + str(counter_test[index]) + '\n'
    tFile = codecs.open('../../report/labeling_result.csv', 'w', 'utf-8')
    tFile.write(lines)
    tFile.close()
    logging.info("Labeling ended at " + str(datetime.datetime.now()))
        
def get_higher_confidence(detection_results):
    chosen_box = None
    max_confidence = -1
    for result in detection_results:
        for box in result.boxes:
            confidence = max(box.conf.tolist())
            if chosen_box is None or max_confidence < confidence:
                chosen_box = box
                max_confidence = confidence
    return chosen_box

def get_bigger_bbox(detection_results):
    chosen_box = None
    max_area = -1
    for result in detection_results:
        for box in result.boxes:
            bbox = box.xywh[0]
            area = float(bbox[2]) * float(bbox[3])
            if chosen_box is None or max_area < area:
                chosen_box = box
                max_area = area
    return chosen_box

def train(category):
    global counter_train, counter_test, counter_val, counter_invalid, finish
    
    index_category = int((categories[category])['id'])
    if index_category == (len(categories)-1): #We dont need to label unknown category
        finish[index_category] = True
        return
    
    count = torch.cuda.device_count()
    device = 'cpu'
    if torch.cuda.is_available():
        logging.debug('Number of GPUs: ' + str(count) + '. \nCUDA ENABLED')
        device = 'cuda'
    resources_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources/")
    model_path = os.path.join(resources_path,"best.pt")
    #model = YOLO("yolo11n.pt").to(device)
    model = YOLO(model_path).to(device)
    model.classes = [8]
    model.agnostic = False  # NMS class-agnostic
    model.multi_label = False
    src_cat_path = os.path.join(DatasetConfig.SRC_FOLDER,category)
    dirs = os.listdir(src_cat_path)
    
    
    must_be_labeled = []
    for imoDir in dirs:
        all_files_processed = []
        filesDownloaded = os.listdir(os.path.join(src_cat_path,imoDir))
        for eachFile in filesDownloaded:
            if ".jpg" in eachFile:
                src_imgPath = os.path.join(src_cat_path,imoDir,eachFile)
                try:
                    img = cv2.imread(src_imgPath)
                except:
                    logging.debug("Error reading image file: " + src_imgPath)
                    continue
                img_width, img_height,channels = img.shape
                if img_height != DatasetConfig.target_img_height or img_width != DatasetConfig.target_img_width: 
                    img_to_process = cv2.resize(img, (DatasetConfig.target_img_width, DatasetConfig.target_img_height), cv2.INTER_AREA)
                else:
                    img_to_process = img
                detection_results = model.predict([img_to_process],verbose=False, conf = 0.1, iou= 0.7)
                chosen_box = get_higher_confidence(detection_results)
                #chosen_box = get_bigger_bbox(detection_results)
                img_name = eachFile.split('.')[0]
                
                if chosen_box is None:
                    counter_invalid [index_category] = counter_invalid [index_category] + 1
                    must_be_labeled.append(eachFile)
                all_files_processed.append([chosen_box,img_to_process,img_name])
                
        total = len(all_files_processed)
        t_train =  int(total * DatasetConfig.TRAIN_PERC)
        c_train =  0
        t_test = int(total * DatasetConfig.TEST_PERC)
        c_test = 0
        t_val = total - (t_train + t_test)
        c_val = 0
        
        for box, img_file,img_name in all_files_processed:
            type = 'train'
            if c_train <= t_train:
                type = 'train'
                counter_train [index_category] = counter_train [index_category] + 1
                c_train =  c_train + 1
            else:
                if c_test < t_test:
                    type = 'test'
                    counter_test [index_category] = counter_test [index_category] + 1
                    c_test =  c_test + 1
                else:
                    type = 'val'
                    counter_val [index_category] = counter_val [index_category] + 1
                    c_val =  c_val + 1
            x=0
            y=0
            width=0
            height=0
            if box is not None:
                bounding_box = box.xyxy[0]
                x = float(bounding_box [0] / DatasetConfig.target_img_width)
                y = float(bounding_box [1] / DatasetConfig.target_img_height)
                width = float(bounding_box [2] / DatasetConfig.target_img_width) - x
                height = float(bounding_box [3] / DatasetConfig.target_img_height) - y
                x = x + (width/2)
                y = y + (height/2)
            dst_yolo_file = os.path.join(root_path,type,"labels",img_name+'.txt')
            line = str(index_category) + ' ' + str(x) + ' ' + str(y) + ' ' + str(width) + ' ' + str(height)
            tFile = codecs.open(dst_yolo_file, 'w', 'utf-8')
            tFile.write(line)
            tFile.close()
            dst_img_file = os.path.join(root_path,type,"images",img_name+'.jpg')
            cv2.imwrite(dst_img_file,img_file)
    
    csv_path=os.path.join(root_path,'csv_results')
    if not os.path.exists(csv_path):
        os.mkdir(csv_path)
    lines = ''
    for file in must_be_labeled:
        lines += file + '\n'
    name_category = (categories[category])['name']
    csv_file=os.path.join(csv_path,name_category+'_unused.csv')
    tFile = codecs.open(csv_file, 'w', 'utf-8')
    tFile.write(lines)
    tFile.close()
    
    finish [index_category] = True

def label(_categories):
    global categories, counter_train, counter_test, counter_val, finish, root_path
    categories = _categories
    root_path = DatasetConfig.ORIGINAL_DATASET_FOLDER
    logging.info("Labeling started at " + str(datetime.datetime.now()))
    train_path = os.path.join(root_path,"train")
    val_path = os.path.join(root_path,"val")
    test_path = os.path.join(root_path,"test")

    if os.path.exists(root_path):
        shutil.rmtree(root_path)
    os.mkdir(root_path)
    if os.path.exists(train_path):
        shutil.rmtree(train_path)
    os.mkdir(train_path)
    os.mkdir(os.path.join(train_path,'images'))
    os.mkdir(os.path.join(train_path,'labels'))
    if os.path.exists(val_path):
        shutil.rmtree(val_path)
    os.mkdir(val_path)
    os.mkdir(os.path.join(val_path,'images'))
    os.mkdir(os.path.join(val_path,'labels'))
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
    os.mkdir(test_path)
    os.mkdir(os.path.join(test_path,'images'))
    os.mkdir(os.path.join(test_path,'labels'))
    threads = []

    for i in range (len(categories)):
        counter_train.append(0)
        counter_test.append(0)
        counter_val.append(0)
        counter_invalid.append(0)
        finish.append(False)

    for cat in categories:
        thread = threading.Thread(target=train, args=(cat,))
        thread.start()
        threads.append(thread)
    show_status()

