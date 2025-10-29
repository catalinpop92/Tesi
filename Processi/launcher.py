import asyncio
from pyzeebe import ZeebeClient
from pyzeebe.channel.insecure_channel import create_insecure_channel
import datetime

# Lista delle città da monitorare (multi-irrigatore)
citta_da_monitorare = ["Berlin", "Paris", "Madrid"]

# Logger su file
def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

# Funzione principale asincrona
async def main():
    # Connessione al broker Zeebe
    channel = create_insecure_channel("localhost:26500")
    client = ZeebeClient(channel)

    # Avvia una istanza del processo per ogni città
    for city in citta_da_monitorare:
        print(f"🚀 Avvio del processo per la città: {city}")
        log(f"Avviata nuova istanza del processo per la città: {city}")

        try:
            await client.run_process(
            bpmn_process_id="Process_02nttud",
            variables={"cityName": city}
            )
        except Exception as e:
            log(f"❌ Errore nell'avvio del processo per {city}: {str(e)}")

    print("✅ Tutti i processi sono stati avviati.")
    log("Avvio batch completato per tutte le città.\n")

# Avvia lo script asincrono
if __name__ == "__main__":
    asyncio.run(main())
