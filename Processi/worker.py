from pyzeebe import ZeebeWorker, Job
from pyzeebe.channel.insecure_channel import create_insecure_channel
import asyncio, datetime, json, os, random
from pyzeebe.errors import BusinessError

STATO_FILE = "stato_irrigatori.json"
LOG_FILE = "log.txt"
ERROR_LOG_FILE = "log_error.txt"

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
        os.fsync(f.fileno())  # Garantisce che venga scritto su disco

def log_errore(m):
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {m}\n")

def log_info(m):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {m}\n")

# ⚠️ NON manteniamo lo stato in memoria: viene caricato ogni volta per coerenza
def attiva_irrigatore(job: Job):
    stato = carica_stato()
    city = job.variables.get("cityName", "sconosciuta")
    now_iso = datetime.datetime.now().isoformat(timespec="minutes")

    if city.lower() == "errorecity" or random.random() < 0.2:
        msg = f"❌ Errore tecnico durante l'attivazione dell'irrigatore a {city}"
        print(msg)
        log_errore(msg)
        raise BusinessError("errore_attivazione", msg)

    stato_corrente = stato.get(city, {}).get("stato", "off")
    if stato_corrente == "on":
        msg = f"ℹ️ L'irrigatore a {city} risulta già attivo"
    else:
        stato[city] = {
            "stato": "on",
            "accensione": now_iso
        }
        salva_stato(stato)
        msg = f"🟢 Irrigatore a {city} attivato con successo (ora: {now_iso})"

    print(msg)
    log_info(msg)

def spegni_irrigatore(job: Job):
    stato = carica_stato()
    city = job.variables.get("cityName", "sconosciuta")

    if city.lower() == "errorecity" or random.random() < 0.2:
        msg = f"❌ Errore tecnico durante lo spegnimento dell'irrigatore a {city}"
        print(msg)
        log_errore(msg)
        raise BusinessError("errore_spegnimento", msg)

    stato_corrente = stato.get(city, {}).get("stato", "off")
    if stato_corrente == "off":
        msg = f"ℹ️ L'irrigatore a {city} risulta già spento"
    else:
        stato[city] = {
            "stato": "off",
            "accensione": None
        }
        salva_stato(stato)
        msg = f"🔴 Irrigatore a {city} spento con successo"

    print(msg)
    log_info(msg)

def invia_notifica(job: Job):
    stato = carica_stato()
    city = job.variables.get("cityName", "sconosciuta")
    dec = job.variables.get("decisionResult", "?")
    errore = job.variables.get("notificaErrore", False)
    stato_attuale = stato.get(city, {}).get("stato", "off")

    if errore:
        msg = f"📨 NOTIFICA ERRORE: Operazione fallita per {city}. Gli irrigatori potrebbero NON essere stati aggiornati correttamente. Controllare manualmente."
        print(msg)
        log_info(msg)
        return

    if dec == "yes":
        msg = f"📨 NOTIFICA: Irrigatori a {city} ACCESI correttamente" if stato_attuale == "on" else f"📨 NOTIFICA: Stato inatteso dopo attivazione per {city}"
    else:
        msg = f"📨 NOTIFICA: Irrigatori a {city} SPENTI correttamente" if stato_attuale == "off" else f"📨 NOTIFICA: Stato inatteso dopo spegnimento per {city}"

    print(msg)
    log_info(msg)

def gestisci_errore(job: Job):
    city = job.variables.get("cityName", "sconosciuta")
    err = job.variables.get("errorMessage", "errore sconosciuto")

    msg = f"📛 GESTIONE ERRORE: Si è verificato un errore durante l'elaborazione per {city}: {err}"
    print(msg)
    log_errore(msg)

    return {"notificaErrore": True}

async def main():
    worker = ZeebeWorker(grpc_channel=create_insecure_channel("localhost:26500"))
    worker.task(task_type="attiva-irrigatore")(attiva_irrigatore)
    worker.task(task_type="spegni-irrigatore")(spegni_irrigatore)
    worker.task(task_type="notifica-email")(invia_notifica)
    worker.task(task_type="gestione-errore")(gestisci_errore)
    await worker.work()

asyncio.run(main())
