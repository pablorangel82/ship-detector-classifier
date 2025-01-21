call conda deactivate sdc-cpu-env
call conda remove -n sdc-cpu-env --all
call conda create -n sdc-cpu-env
call conda activate sdc-cpu-env
call conda install pytorch
pip install -r ../requirements-cpu.txt
