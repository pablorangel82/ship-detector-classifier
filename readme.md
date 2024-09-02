# Environment preparation

## With CUDA support (Windows 10 PRO):

- Install Python 3.10.11. Let Python installer set Python PATH automatically
- Update drivers de GPU NVIDIA® to 450.80.02 or higher.
- Install CUDA Development Kit 12.3.2
- Install CUDNN 8.9.7
- Copy folders and files from CUDNN path to same folders of CUDA Development Kit path
- execute create-env-gpu using windows cmd

## Without CUDA support
- Python 3.10.11. Let Python installer set Python PATH automatically
- execute create-env-cpu using windows cmd

# Running and viewing

- You need a json file with calibration and camera features data. The source can be a local file or rstp address. 
- There is a variable called FORCED_DELAY in main.py. Use only if the source is a local file, with the frame rate in seconds (eg. 30 fps -> 0.03 seconds). Otherwise, set value to 0.
- Video frame and bounding boxes are available for web-viewers consuming from localhost (8000 port) REST service.