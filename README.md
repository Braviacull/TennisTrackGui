# TennisTrackGui

# Instructions to create and set up an environment to use the program on Windows:

<!-- 
IMPORTANT: If you have trouble installing catboost, you probably need to install Rust first. Alternatively, you can install an older version of Python (3.12.7 and 3.12.8 should be fine).

IMPORTANT: always use pip to install packages.

IMPORTANT: On Windows, use cmd (I couldn't get conda to work on PowerShell for some reason).

IMPORTANT: with python 3.10 I had problems with person detection

* RECCOMENDED (If you have a CUDA-compatible GPU and intend to use it). 
-->

1) Install conda (or miniconda). We will use it only to create and activate the environment.
2) Run conda create --name tennis or any other name you want to give to your environment.
3) Run conda activate tennis or any other name chosen in the previous step.
4) Run conda config --set auto_update_conda False
5) Run conda install python=3.12.8 or any other version you prefer
6) Run python --version
7) * Update NVIDIA drivers (preferably studio version).
8) * Install compatible CUDA Toolkit and PyTorch (check the PyTorch website).
9) Run pip install -r text_files/requirements.txt
10) * Run python tests/cudaTest.py (if it returns True, then everything went well and the GPU will be used for calculations).11) install vlc media player (make sure is the 64 bit version)

# SIDE NOTES
1) App Icon made by Ina Mella from www.flaticon.com


<!-- per aggiornare la cache di vlc -->
<!-- "C:\Program Files\VideoLAN\VLC\vlc-cache-gen.exe" "C:\Program Files\VideoLAN\VLC\plugins" -->
