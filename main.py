import cv2

thres = 0.5 # Threshold to detect object

cap = cv2.VideoCapture('samples/military.mp4')
cap.set(3,1280)
cap.set(4,720)
cap.set(10,70)

classNames= []
classFile = 'classifier/ship_types'
with open(classFile,'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

configPath = 'detector/detector.pbtxt'
classifier = 'classifier/model.pb'
detector = 'detector/detector.pb'

netClassifier = cv2.dnn.readNetFromTensorflow(classifier)
netDetector = cv2.dnn_DetectionModel(detector,configPath)
netDetector.setInputSize(224,224)
netDetector.setInputScale(1.0/ 127.5)
netDetector.setInputMean((127.5, 127.5, 127.5))
netDetector.setInputSwapRB(True)

while True:
    success,img = cap.read()
    classIds, confs, bbox = netDetector.detect(img,confThreshold=thres)
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):

            if classId == 9:
                x = box[0]
                y = box[1]
                w = box[2]
                h = box[3]

                name = 'Unknown'
                max_value = 0

                # if w >= 224 and h >= 224:
                vessel_img = img[y:y+h, x:x+w]
                vessel_img = cv2.resize(vessel_img, (224, 224))
                new_img = cv2.normalize(vessel_img, None, 0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
                netClassifier.setInput(cv2.dnn.blobFromImage(new_img, size=(224, 224), swapRB=True, crop=False))
                preds = netClassifier.forward()
                max_index = 0
                max_value = preds[0][0]
                for i in range(len(preds[0])):
                    if max_value < preds[0][i]:
                        max_index = i
                        max_value = preds[0][i]
                name = classNames[max_index]
                cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                cv2.putText(img,name.upper(),(box[0]+10,box[1]+30),
                            cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                cv2.putText(img,str(round(max_value*100,2)),(box[0]+200,box[1]+30),
                            cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

    cv2.imshow('Ship Detector', cv2.resize(img, (1280,720)))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
