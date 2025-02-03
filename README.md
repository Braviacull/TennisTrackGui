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
2) * Update NVIDIA drivers (preferably studio version).
3) * Install compatible CUDA Toolkit and PyTorch (check the PyTorch website).
4) * Run python cudaTest.py (if it returns True, then everything went well and the GPU will be used for calculations).
5) conda create --name tennis or any other name you want to give to your environment.
6) conda activate tennis or any other name chosen in the previous step.
7) pip install PySide6
8) pip install opencv-python
9) pip install -r requirements.txt

# VERSIONE IN ITALIANO

# Istruzioni per creare e settare un ambiente in cui poter usare il programma su Windows:

<!-- 
IMPORTANTE: Se hai problemi ad installare catboost, probabilmente hai bisogno di installare rust prima.
In alternativa, puoi installare una vecchia versione di python (3.12.7 dovrebbe andare bene)

IMPORTANTE: se ad un certo punto, qualcosa non dovesse funzionare, riavviare il sistema può essere una soluzione.

IMPORTANTE: usa sempre pip per installare i pacchetti.

IMPORTANTE: usa cmd, non usare powershell (non sono riuscito a far funzionare conda su powershell per qualche motivo).

* Se si dispone di una gpu cuda compatible e si intende utilizzarla. 
-->
1) Installa conda (o miniconda). Lo useremo soltanto per creare e attivare l'ambiente.
2) * Aggiorna i driver di NVIDIA (versione studio preferibilmente).
3) * Installa Cuda Toolkit e pytorch compatibili  (controlla sul sito di pytorch).
4) * lancia python cudaTest.py (se restituisce True, allora é andato tutto bene e verrà usata la gpu per i calcoli).
5) conda create --name tennis o qualsiasi altro nome vuoi dare al tuo ambiente.
6) conda activate tennis o qualsiasi altro nome scelto allo step precedente.
7) pip install PySide6
8) pip install opencv-python
9) pip install -r requirements.txt

# SIDE NOTES
1) App Icon made by Ina Mella from www.flaticon.com