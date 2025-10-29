import schedule
import time
import subprocess
import datetime

# Logger su file
def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

# Funzione che lancia il processo
def run_launcher():
    try:
        log("⏳ Avvio automatico del launcher.py per il controllo periodico degli irrigatori.")
        subprocess.run(["python", "launcher.py"], check=True)
        log("✅ Completato ciclo di avvio periodico.")
    except subprocess.CalledProcessError as e:
        log(f"❌ Errore nell'esecuzione di launcher.py: {e}")

# Avvia ogni 30 minuti
schedule.every(5).minutes.do(run_launcher)

log("🔁 Scheduler avviato: controllo ogni 30 minuti.\n")
print("🔁 Scheduler avviato: controllo ogni 30 minuti. Premi Ctrl+C per interrompere.")

while True:
    schedule.run_pending()
    time.sleep(1)
