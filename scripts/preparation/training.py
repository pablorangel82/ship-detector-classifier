from ultralytics import YOLO
import torch
import torch.nn as nn

resume = False

if resume == True:
    model = YOLO("runs/detect/train13/weights/last.pt")
else:
    model = YOLO("yolo11m.pt")

count = torch.cuda.device_count()
device = "cpu"    

print('Number of GPUs: ' + str(count))
if torch.cuda.is_available():
    print('CUDA ENABLED')
    if count >= 1:
        device = [0]
  
# Train the model
if __name__ == '__main__':
    results = model.train(data="resources/data.yaml", cls = 0.7, save_period=30, conf = 0.2, batch= 8, resume = resume, device=device,epochs=200)

