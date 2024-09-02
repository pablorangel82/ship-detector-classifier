from ultralytics import YOLO
import torch

count = torch.cuda.device_count()
print('Number of GPUs: ' + str(count))
device = 'cpu'
if torch.cuda.is_available():
    print('CUDA ENABLED')
    device = 'cuda'

# Load a model
model = YOLO("yolov8n.pt").to(device)

# Train the model
if __name__ == '__main__':
    results = model.train(data="dataset/data.yaml", epochs=100)