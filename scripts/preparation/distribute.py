import os
import codecs
import datetime
import logging

import shutil

def distribute():
    root_path = 'D:\\dataset'
    logging.info("Distributing started at " + str(datetime.datetime.now()))
    train_path = os.path.join(root_path,"train")
    val_path = os.path.join(root_path,"val")
    test_path = os.path.join(root_path,"test")

    os.mkdir(train_path)
    os.mkdir(os.path.join(train_path,'images'))
    os.mkdir(os.path.join(train_path,'labels_v1'))
    os.mkdir(val_path)
    os.mkdir(os.path.join(val_path,'images'))
    os.mkdir(os.path.join(val_path,'labels_v1'))
    os.mkdir(test_path)
    os.mkdir(os.path.join(test_path,'images'))
    os.mkdir(os.path.join(test_path,'labels_v1'))
    
    files = []
    for i in range(26):
        files.append([])

    allFiles = os.listdir(root_path)

    for eachFile in allFiles:
        if ".txt" in eachFile:
            src_label_path = os.path.join(root_path,eachFile)
            label_file = codecs.open(src_label_path, 'r', 'utf-8')
            line = label_file.read()
            label_file.close()
            data = line.split(' ')
            try:
                cat = int(data[0])
                file_name = eachFile.split('.')[0]
                files [cat].append([file_name+'.txt',file_name+'.jpg'])
            except:
                logging.info('Error reading file: ' + str(eachFile))
    
    for i in range(len(files)):
        files_per_category = files [i]
        t_train =  0
        c_train =  0
        t_test = 0
        c_test = 0
        t_val = 0
        c_val = 0
        for label, img in files_per_category:
            total = len(files_per_category)
            t_train =  int(total * 0.7)
            t_test = int(total * 0.15)
            t_val = total - (t_train + t_test)
            type = 'train'
            if c_train <= t_train:
                type = 'train'
                c_train =  c_train + 1
            else:
                if c_test < t_test:
                    type = 'test'
                    c_test =  c_test + 1
                else:
                    type = 'val'
                    c_val =  c_val + 1
            src_path_img = os.path.join(root_path,img)
            dst_path_img = os.path.join(root_path,type,'images',img)
            src_path_label = os.path.join(root_path,label)
            dst_path_label = os.path.join(root_path,type,'labels_v1',label)
            try:
                shutil.copy(src_path_label,dst_path_label)
                shutil.copy(src_path_img,dst_path_img)
            except:
                logging.info("It was not possible to copy file: " + label)

        logging.info("Category: " + str(i))
        logging.info("# Total files: " + str(total))
        logging.info("# train files: " + str(c_train))
        logging.info("# test files: " + str(c_test))
        logging.info("# val files: " + str(c_val))
