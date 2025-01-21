import cv2
from dataset_config import DatasetConfig
import os
from category_en import categories

train_path = os.path.join(DatasetConfig.DATASET_FOLDER,"train")
val_path = os.path.join(DatasetConfig.DATASET_FOLDER,"val")
test_path = os.path.join(DatasetConfig.DATASET_FOLDER,"test")

def get_name(id):
    for cat in categories:
        _id = int(categories[cat]['id'])
        if id == _id:
            return categories[cat]['name']

def show ():
    img_files = os.listdir(os.path.join(train_path,'images'))
    label_files = os.listdir(os.path.join(train_path,'labels'))                       
    for f in img_files:
        file_name = f.split('.')[0]
        img_path = os.path.join(train_path,'images',file_name+'.jpg')
        label_path = os.path.join(train_path,'labels',file_name+'.txt')
        image = cv2.imread(img_path)
              
        with open(label_path,  'r') as txt:
            ship_data=""
            for line in txt:
                line.replace("\n","")
                ship_data = ship_data + line
            data = ship_data.split(" ")
            show_image(image,data)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def show_image(image, data):
    x = int(float(data [1]) * DatasetConfig.target_img_width)
    y = int(float(data [2]) * DatasetConfig.target_img_height)
    w = int(float(data [3]) * DatasetConfig.target_img_width)
    h = int(float(data [4]) * DatasetConfig.target_img_height) 
    x = int(x - (w /2)) 
    y = int(y - (y /2))
    name = get_name(int(data[0]))
    image_drawn = cv2.rectangle(image, (x,y), (x+w,y+h),(0, 255, 0),1)
    image_drawn = cv2.putText(image_drawn,name,(x-10,y-10),cv2.FONT_HERSHEY_SIMPLEX,1,(0, 255, 0), 1, cv2.LINE_AA )    
    cv2.imshow("YOLO Annotation",image_drawn)
    cv2.waitKey(0)
