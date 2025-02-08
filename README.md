# TennisTrackGui

# ENGLISH VERSION

# Instructions to create and set up an environment to use the program on Windows:

<!-- 
IMPORTANT: If you have trouble installing catboost, you probably need to install Rust first.
Alternatively, you can install an older version of Python (3.12.7 should be fine).

IMPORTANT: if at any point something doesn't work, restarting the system can be a solution.

IMPORTANT: always use pip to install packages.

IMPORTANT: use cmd, do not use PowerShell (I couldn't get conda to work on PowerShell for some reason).

* If you have a CUDA-compatible GPU and intend to use it. 
-->
1) Install conda (or miniconda). We will use it only to create and activate the environment.
2) conda create --name tennis or any other name you want to give to your environment.
3) conda activate tennis or any other name chosen in the previous step.
4) * Update NVIDIA drivers (preferably studio version).
5) * Install compatible CUDA Toolkit and PyTorch (check the PyTorch website).
6) * Run python tests/cudaTest.py (if it returns True, then everything went well and the GPU will be used for calculations).
7) pip install PySide6
8) pip install opencv-python
9) pip install -r text_files/requirements.txt
10) install vlc media player (make sure is the 64 bit version)

# SIDE NOTES
1) App Icon made by Ina Mella from www.flaticon.com