from preparation.dataset_config import DatasetConfig
import os
import json
import datetime
import logging
import threading
import time
import codecs
import math

vessels_data = []
categories = None
root_path = None

def save_results():
    global categories, vessels_data
    lines = ''
    total_samples = 0
    for cat in categories:
        name = (categories[cat])['name']
        sum_width = 0
        sum_length = 0
        sum_draugth = 0
        sum_summerdwt = 0
        avg_width = 0
        avg_length = 0
        avg_draught = 0
        avg_summerdwt = 0
        index = int ((categories[cat])['id'])
        if index == 26:
            continue
        logging.info('\n\nCategory:' + cat)

        number_of_samples = len(vessels_data[index])
        total_samples = total_samples + number_of_samples
        regs = ''

        for entry in vessels_data [index]:
            sum_length += entry[0]
            sum_draugth += entry[1]
            sum_width += entry[2]
            sum_summerdwt += entry[2]
            reg = str(entry[0]) + ',' + str(entry[1]) + ',' + str(entry[2]) + ',' + str(entry[3]) + '\n'
            regs = regs + reg

        tFile = codecs.open('../../report/statistics/statistics_'+ name +'.csv', 'w', 'utf-8')
        tFile.write(regs)
        tFile.close()
       
        avg_length = sum_length/number_of_samples
        avg_width = sum_width/number_of_samples
        avg_draught = sum_draugth/number_of_samples
        avg_summerdwt = sum_summerdwt / number_of_samples
        sum_width = 0
        sum_length = 0
        sum_draugth = 0
        sum_summerdwt = 0
        for entry in vessels_data [index]:
            sum_length += (entry[0] - avg_length) ** 2
            sum_draugth += (entry[1]  - avg_draught) ** 2
            sum_width += (entry[2]  - avg_width) ** 2
            sum_summerdwt += (entry[3]  - avg_summerdwt) ** 2
        mean_deviation_width = math.sqrt (sum_width / number_of_samples)
        mean_deviation_length = math.sqrt (sum_length / number_of_samples)    
        mean_deviation_draught = math.sqrt (sum_draugth / number_of_samples)
        mean_deviation_summerdwt = math.sqrt (sum_summerdwt / number_of_samples)

        coef_var_length = ((mean_deviation_length / avg_length) * 100)
        coef_var_draught = ((mean_deviation_draught / avg_draught) * 100)
        coef_var_width = ((mean_deviation_width / avg_width) * 100)
        coef_var_summerdwt = ((mean_deviation_summerdwt / avg_summerdwt) * 100)
        
        #lines += name + ', ' + str(number_of_samples) + str(avg_length) + ', ' + str(coef_var_length) + ', ' + str(mean_deviation_length) + ', ' + str(avg_draught) + ', ' + str(coef_var_draught) + ', ' + str(mean_deviation_draught) + ', ' + str(avg_width) + ', '+ str(coef_var_width) + ', ' + str(mean_deviation_width) + ', ' + str(avg_summerdwt) + ', '+ str(coef_var_summerdwt) + ', ' + str(mean_deviation_summerdwt)+'\n'
        lines += name + ', ' + str(number_of_samples) + ', ' + str(avg_draught) + ', ' + str(coef_var_draught) + ', ' + str(mean_deviation_draught) +'\n'


        logging.info('Average length: ' + str(avg_length) + ' - Coef Var: ' + str(coef_var_length) + ' - Number of Samples: ' + str(number_of_samples) + '- Standard deviation: ' + str(mean_deviation_length))
        logging.info('Average draugth: ' + str(avg_draught) + ' - Coef Var: ' + str(coef_var_draught) + ' - Number of Samples: ' + str(number_of_samples) + ' - Standard deviation: ' + str(mean_deviation_draught))
        logging.info('Average width: ' + str(avg_width) + ' - Coef Var: ' + str(coef_var_width) + ' - Number of Samples: ' + str(number_of_samples) + ' - Standard deviation: ' + str(mean_deviation_width))
        logging.info('Average summerdwt: ' + str(avg_summerdwt) + ' - Coef Var: ' + str(coef_var_summerdwt) + ' - Number of Samples: ' + str(number_of_samples) + ' - Standard deviation: ' + str(mean_deviation_summerdwt))

    tFile = codecs.open('../../report/statistics/statistics.csv', 'w', 'utf-8')
    tFile.write(lines)
    tFile.close()
    logging.info('Total samples: '+str(total_samples))
    logging.info("Statistics ended at " + str(datetime.datetime.now()))

def extract_dimensions(category):
    index_category = int((categories[category])['id'])
    if index_category == (len(categories)-1): #We can avoid unknown category
        return
    global vessels_data

    src_cat_path = os.path.join(DatasetConfig.SRC_FOLDER,category)
    dirs = os.listdir(src_cat_path)
    
    for imoDir in dirs:
        filesDownloaded = os.listdir(os.path.join(src_cat_path,imoDir))
        for eachFile in filesDownloaded:
            if ".json" in eachFile:
                src_json_path = os.path.join(src_cat_path,imoDir,eachFile)
                json_file = open(src_json_path)
                vessel_data = json.load(json_file)
                length = vessel_data['length']
                draught = vessel_data['draugth']
                width = vessel_data['width']
                summerdwt = vessel_data['summer_dwt']
                if length is not None and draught is not None and width is not None and summerdwt is not None:
                    vessels_data [index_category].append([length,draught,width,summerdwt])
            

def collect(_categories):
    global categories, root_path, vessels_data
    categories = _categories
    root_path = DatasetConfig.DATASET_FOLDER
    logging.info("Statistics calculations started at " + str(datetime.datetime.now()))
    threads = []

    for cat in categories:
        vessels_data.append([])
        thread = threading.Thread(target=extract_dimensions, args=(cat,))
        thread.start()
        threads.append(thread)
    threads[0].join()

    save_results()