# TennisTrackGui

# Istruzioni per creare e settare un ambiente in cui poter usare il programma su Windows:

<!-- 
IMPORTANTE: se ad un certo punto, qualcosa non dovesse funzionare, riavviare il sistema può essere una soluzione.

IMPORTANTE: usa sempre pip per installare i pacchetti.

IMPORTANTE: usa cmd, non usare powershell (non sono riuscito a far funzionare conda su powershell per qualche motivo).

* Se si dispone di una gpu cuda compatible e si intende utilizzarla. 
-->

0) installa la versione più recente di python.

1) Installa conda (o miniconda). Lo useremo soltanto per creare e attivare l'ambiente.
2) * Aggiorna i driver di NVIDIA (versione studio preferibilmente).
3) * Installa Cuda Toolkit e pytorch compatibili  (controlla sul sito di pytorch).
4) * lancia python cudaTest.py (se restituisce True, allora é andato tutto bene e verrà usata la gpu per i calcoli).
5) conda create --name tennis o qualsiasi altro nome vuoi dare al tuo ambiente.
6) conda activate tennis o qualsiasi altro nome scelto allo step precedente.
7) pip install PySide6
8) pip install opencv-python
9) pip install -r requirements.txt