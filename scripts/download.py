from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import datetime
import logging
import codecs
import os
import re
import json
import time
import shutil
from dataset_config import DatasetConfig
from category_en import categories
import cv2
import threading
import numpy as np 

attempts_limit = 5
resize = True
total_expected = 0
total_downloaded = 0
total_errors = 0

errors_list = []

def request(url):
    logging.debug("Getting from: " + url)
    attempts = 0
    req = None
    con = None
    while attempts <= attempts_limit:
        try:
            time.sleep(1 * attempts)
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            con = urlopen(req, timeout=1000)
            attempts = attempts_limit + 1
        except Exception as exception:
            if attempts > attempts_limit:
                logging.info('Cannot able to download content.')
                return None
            logging.info("Connection error. Trying again: " + str(attempts))
            attempts = attempts +1
    response = con.read()
    return response

def html_to_json(html):
    soup = BeautifulSoup(html, "lxml")
    values = None
    tags = [tg for tg in soup.findAll('script')]
    scripts = [each.getText() for each in tags]
    for each in scripts:
        if each is None:
            continue
        start = each.find("window._INITIAL_DATA")
        if start != -1:
            start = each.find("=",start,len(each)) +1
            end = each.rfind(";",start,len(each))
            json_value = each[start:end]
            values  = json.loads(json_value)
            break
    return values

def save_image(url,path,file):
    content = request(url)
    if content is None:
        return False
    logging.debug("Saving image at: " + path)
    if not os.path.exists(path):
        os.mkdir(path)
    path = os.path.join(path, file)
    img = np.asarray(bytearray(content), dtype="uint8")
    img = cv2.imdecode(img,cv2.IMREAD_COLOR)
    if resize == True:
        img = cv2.resize(img, (DatasetConfig.target_img_width, DatasetConfig.target_img_height), cv2.INTER_AREA)
    cv2.imwrite(path,img)
    return True

def save_data(eni, category, outFolder):
    _id = int(re.sub('[^0-9]', '', eni))
    url = DatasetConfig.SRC_LINK + str(_id)
    
    html=request(url)
    if html is None:
        return False
    json_values = html_to_json(html)
    
    if json_values is not None:
        try:
            page_data = json_values['page_data']
            ship_data = page_data['ship_data']
            imo = str(ship_data ['imo_no'])
        except Exception:
            global errors_list
            errors_list.append(eni)
            logging.info('Data not available: ' + str (eni))
            return False
        path = f'%s' % os.path.join(outFolder, imo)
        if not os.path.exists(path):
            os.mkdir(path)
        number_of_files = len(os.listdir(path))
        path_meta_data = os.path.join(path, imo+'.json')
        more = page_data ['more_of_this_ship']
        photos = more['items']
        if (len(photos) +2) <= number_of_files:
            logging.info('Data already downloaded: ' + str(imo))
            return True
        else:
            logging.info('Expected: ' + str(len(photos) +2) + '. Found: ' + str(number_of_files))
        past = []
        logging.debug(url)
        main_photo = page_data['photo']
        photos.append(main_photo)
        
        for h in photos:
            lid = str(h['lid'])
            url_full_image = DatasetConfig.SRC_LINK + 'big/' + lid[len(lid)-1] + '/' + lid[len(lid)-2] + '/' + lid[len(lid)-3]+'/'+lid+'.jpg'
            url_photographer = DatasetConfig.SRC_LINK +lid
            photographer = 'Not available'
            try:
                html_photo_details = request(url_photographer)
                if html_photo_details is not None:
                    json_values_photo_details = html_to_json(html_photo_details)
                    if json_values_photo_details is not None:
                        former_details = (json_values_photo_details ['page_data'])['ship_data']
                        photographer = (json_values_photo_details['page_data'])['print_photographer']
                        former = {
                            "lid":lid,
                            "mmsi":former_details['mmsi_code'],
                            "name":former_details['name'],
                            "callsign":former_details['call_sign'],
                            "flag":former_details['flag'],
                            "photographer":photographer
                        }
                    past.append(former)
            except:
                logging.info("Former informations are not available. ")
            save_image(url_full_image,path,lid+'.jpg')
        logging.debug("Saving metadata at: " + path)
        meta_data = {
            "imo":imo,
            "category":category,
            "length":ship_data['length'],
            "draugth":ship_data['draught'],
            "width":ship_data['beam'],
            "gross_tonnage":ship_data['gross_tonnage'],
            "builder":ship_data['builder'],
            "manager":ship_data['manager'],
            "owner":ship_data['owner'],
            "build_date":ship_data['build'],
            "summer_dwt":ship_data['summer_dwt'],
            "past":past
        }
        
        tFile = codecs.open(path_meta_data, 'w', 'utf-8')
        tFile.write(json.dumps(meta_data) + '\n')
        tFile.close()
        return True
    return False
        

def worker(eni_list):
    if eni_list is None or len(eni_list) == 0:
        return 
    currFolder = os.path.join(DatasetConfig.SRC_FOLDER,eni_list[0][1]) 
    if not os.path.exists(currFolder):
        os.mkdir(currFolder)
    global total_downloaded
    global total_errors
    for eni, category in eni_list:
        try:
            ret = save_data(eni, category, currFolder)
            if ret == True:
                total_downloaded = total_downloaded + 1
            else:
                total_errors = total_errors + 1
        except:
            logging.info('Unknown error.')
            total_errors = total_errors + 1
            

def show_status():
    while (total_downloaded+total_errors) < total_expected:
        logging.info('Downloaded ' + str(total_downloaded) + ' of ' + str(total_expected) + ' files. Errors: ' + str(total_errors) + '. Processed: ' + str(total_errors+total_downloaded) )
        time.sleep(5)
    logging.info('Saving ships not found...')
    path = os.path.join(DatasetConfig.SRC_FOLDER,"error.txt")
    tFile = codecs.open(path, 'w', 'utf-8')
    for eni in errors_list:
        tFile.write(eni + '\n')
    tFile.close()


def download (start_again, auto_resize):
    global resize
    resize = auto_resize
    logging.info("Downloading started at " + str(datetime.datetime.now()))
    if start_again:
        logging.info("Downloading everything again " + str(datetime.datetime.now()))
        shutil.rmtree(DatasetConfig.SRC_FOLDER)
    else:
        logging.info("Downloading only missing data " + str(datetime.datetime.now()))
    if not os.path.exists(DatasetConfig.SRC_FOLDER):
        os.mkdir(DatasetConfig.SRC_FOLDER)
    if resize == True:
        logging.info('Auto resize enable to: ' + str(DatasetConfig.target_img_width) + ' x ' + str(DatasetConfig.target_img_width))
    else:
        logging.info('Auto resize is disable. You should read copyright policies of shipspotting: https://www.shipspotting.com/support/68')

    downloadFile = codecs.open(DatasetConfig.ENI_LIST, "r", "utf-8")
    downloadContent = downloadFile.readlines()
    downloadFile.close()
    eni_per_category = []
    for i in range (len(categories)):
        eni_per_category.append([])

    for index, eachLine in enumerate(downloadContent):
        temp = []
        temp.append (eachLine.split(',')[0])
        cat = eachLine.split(',')[3]
        for y in ['\n', '\t','\r', '\'']:
            cat = cat.replace(y, "")
        cat = cat.replace('/', " ")
        temp.append (cat)
        index = int ((categories[cat])['id'])
        eni_per_category [index].append(temp)
    global total_expected    
    for i in range (len(categories)):
        total_expected = total_expected + len(eni_per_category [i])
        thread = threading.Thread(target=worker, args=(eni_per_category [i],))
        thread.start()

    show_status()