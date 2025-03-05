from ultralytics import YOLO
import torch

resume = True

if resume == True:
    model = YOLO("runs/detect/train13/weights/last.pt")
else:
    model = YOLO("yolo11n.pt")

count = torch.cuda.device_count()
device = "cpu"    

print('Number of GPUs: ' + str(count))
if torch.cuda.is_available():
    print('CUDA ENABLED')
    if count >= 2:
        device = [0,1]
  
# Train the model
if __name__ == '__main__':
    results = model.train(data="resources/data.yaml", resume = resume, device=device,batch=150,epochs=500)

