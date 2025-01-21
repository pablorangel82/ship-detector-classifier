conda create -n sdc-gpu-env
conda activate sdc-gpu-env
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
pip install -r ../requirements-gpu.txt
