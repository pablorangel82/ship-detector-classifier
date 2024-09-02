call conda create -n sdc-gpu-env
call conda activate sdc-gpu-env
call conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
pip install -r requirements-gpu.txt
