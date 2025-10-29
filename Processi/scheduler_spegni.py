# scheduler_spegnimento.py
import schedule
import time
import subprocess
import datetime
import sys

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def run_spegni():
    result = subprocess.run(
        [sys.executable, "spegni_irrigatori.py"],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()
    error = result.stderr.strip()

    if result.returncode == 0 and output:
        print(output)
        log(f"⚙️ Spegnimento automatico eseguito:\n{output}\n")

    elif result.returncode != 0:
        log(f"❌ Errore nell'esecuzione di spegni_irrigatori.py:\nExit code: {result.returncode}\nStderr: {error}\n")

# Pianifica ogni 3 minuti
schedule.every(3).minutes.do(run_spegni)

print("🔁 Scheduler avviato: controllo spegnimenti automatici ogni 3 minuti. Premi Ctrl+C per interrompere.")

while True:
    schedule.run_pending()
    time.sleep(1)
