
# COMANDI PER AVVIARE DIVERSE PARTI DI CODICE

# MAIN PROGETTO ORIGINALE:
python main.py --path_ball_track_model "model_best.pt"  --path_court_model "model_tennis_court_det.pt"  --path_bounce_model "ctb_regr_bounce.cbm"  --path_input_video "C:\Users\aless\OneDrive - University of Pisa\Studio\studio in corso\tirocinio\TennisTrackGui\Inputs\djok2.mp4"  --path_output_video "C:\Users\aless\Desktop\output.mp4"

python scene_detect_test.py --path_input_video "C:\Users\Alessio\Desktop\input\sinner10sec.mp4"  --path_output_video "C:\Users\Alessio\Desktop\output\sinner.mp4"

# MAIN MIO RIMUOVI PUBBLICITÀ:
python main.py --path_court_model "model_tennis_court_det.pt"  --path_input_video "C:\Users\Alessio\Desktop\input\sinner.mp4"  --path_output_video "C:\Users\Alessio\Desktop\output\sinner.mp4"

# IMPORTANTE : conda activate myenv

conda activate tennis
cd "C:\Users\Alessio\OneDrive - University of Pisa\Documenti\Github clones\Tennis\TennisTrackGui"

# COMANDI PER AGGIORNARE REPO

git status

git add .

git commit -m "Descrizione delle modifiche"

# Prima di fare il push, è buona pratica controllare se ci sono modifiche sul remoto:
git pull origin main --rebase

git push origin main
