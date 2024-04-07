import cv2
import filters

thres = 0.42 # Threshold to detect object
width = 1280
height = 720
crop_inc = 10
crop_max = 224

cap = cv2.VideoCapture('samples/test2.mp4')
cap.set(3,width)
cap.set(4,height)
cap.set(10,70)

classNames= []
classFile = 'classifier/ship_types-ptbr'
with open(classFile,'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

configClassifier = 'detector/detector.pbtxt'
thres_detection = 0.6
thres_classifier = 0.6
classifier = 'classifier/model.pb'
detector = 'detector/detector.pb'

netClassifier = cv2.dnn.readNetFromTensorflow(classifier)
netDetector = cv2.dnn_DetectionModel(detector,configClassifier)
netDetector.setInputSize(224,224)
netDetector.setInputScale(1.0/ 127.5)
netDetector.setInputMean((127.5, 127.5, 127.5))
netDetector.setInputSwapRB(True)

while True:
    success,img = cap.read()
    img_to_show = img.copy()
    classIds, confs, bbox = netDetector.detect(img_to_show,confThreshold=thres)

    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):

            if classId == 9 and confidence > thres_detection:
                x = box[0]
                y = box[1]
                w = box[2]
                h = box[3]

                x = x - int(w * 0.25)
                y = y - int(h * 0.25)
                size_w = int(w * 1.70)
                size_h = int(h * 1.70)

                if x < 0:
                    x = 0
                if y < 0:
                    y = 0

                name = classNames [5]
                max_value = 0
                vessel_img = img[y:y+size_h, x:x+size_w]
                # vessel_img = filters.enhanced_image_sharpness(vessel_img)
                method = cv2.INTER_CUBIC
                if w > crop_max or h > crop_max:
                    method = cv2.INTER_AREA
                vessel_img = filters.image_resize(vessel_img, crop_max, crop_max, method, False)
                # cv2.imshow('Ship Detector', vessel_img)
                new_img = cv2.normalize(vessel_img, None, 0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
                netClassifier.setInput(cv2.dnn.blobFromImage(new_img, size=(crop_max, crop_max), swapRB=True, crop=False))
                preds = netClassifier.forward()
                max_index = 0
                max_value = preds[0][0]
                for i in range(len(preds[0])):
                    if max_value < preds[0][i]:
                        max_index = i
                        max_value = preds[0][i]
                if max_value > thres_classifier:
                    name = classNames[max_index]
                cv2.rectangle(img_to_show, [x,y,size_w,size_h], color=(0, 0, 255), thickness=1)
                cv2.putText(img_to_show,name.upper()+'('+str(round(max_value * 100))+')',(x-10,y-10),
                            cv2.FONT_HERSHEY_COMPLEX,0.7,(0,0,255),1)

    cv2.imshow('Ship Detector', img_to_show)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
