import json, os, datetime
import sys

STATO_FILE = "stato_irrigatori.json"
LOG_FILE = "log.txt"
MAX_ACCENSIONE_MINUTI = 3  # Cambialo a 3 per test rapido

def carica_stato():
    if os.path.exists(STATO_FILE):
        try:
            return json.load(open(STATO_FILE, encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}

def salva_stato(stato):
    with open(STATO_FILE, "w", encoding="utf-8") as f:
        json.dump(stato, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())

def log_info(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

def spegni_irrigatori_troppo_vecchi():
    stato = carica_stato()
    now = datetime.datetime.now()
    modificato = False

    for city, dati in stato.items():
        if isinstance(dati, dict) and dati.get("stato") == "on" and "accensione" in dati and dati["accensione"]:
            try:
                accensione = datetime.datetime.fromisoformat(dati["accensione"])
                minuti_passati = (now - accensione).total_seconds() / 60
                if minuti_passati > MAX_ACCENSIONE_MINUTI:
                    stato[city]["stato"] = "off"
                    stato[city]["accensione"] = None
                    msg_console = f"[SPEGNIMENTO] {city} acceso da {int(minuti_passati)} minuti"
                    msg_log = f"⏱️ Spegnimento automatico: irrigatore a {city} acceso da {int(minuti_passati)} minuti"
                    print(msg_console)
                    log_info(msg_log)
                    modificato = True
            except Exception as e:
                print(f"[ERRORE PARSING] {city}: {e}")

    if modificato:
        salva_stato(stato)

if __name__ == "__main__":
    try:
        spegni_irrigatori_troppo_vecchi()
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERRORE ESECUZIONE SCRIPT] {e}")
        sys.exit(1)
