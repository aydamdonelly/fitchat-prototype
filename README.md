# FitChat-Prototyp

Der Bot soll dazu dienen, erste Funktionalitäten für den FitChat lokal laufen zu lassen und implementiert zu bekommen, sodass sie präsentierbar sind. Der Conversation Flow sowie das Speichern und Verarbeiten der Daten stehen hierbei im Vordergrund. Andere Funktionalitäten, wie das Verarbeiten mehrerer Nachrichten auf WhatsApp, die eigentlich eine Prompt losschicken sollen, folgen später.

## Einrichtung

Für die Einrichtung ist es nötig, eine `pipenv`-Umgebung einzurichten, mit der die `run.py` ausgeführt werden kann.

```sh
   pipenv shell
   python3 run.py
```

Zudem muss auf der "Meta for Developers"-Plattform eine App erstellt werden. Der API-Key dieser App wird in die `.env` (siehe `example.env`) in `ACCESS_TOKEN` eingetragen. Auch andere Informationen wie die `APP_ID` sind hier notwendig. Anschließend muss ein Webhook erstellt werden. Der Secret-Key, der hier angegeben wird, muss mit dem in der `.env` übereinstimmen.

### Schritte zur Einrichtung

1. **Erstellen einer Serveo-Adresse**

   ```sh
   ssh -R 80:localhost:8000 serveo.net
   ```

   Der angegebene Port bei Localhost muss mit dem in `run.py` übereinstimmen. Der Link, der dir hier ausgegeben wird, wird dann mit dem Suffix `/webhook` ergänzt. Nun kann die Webhook gespeichert werden. Serveo down? Alternativ kann auch http://localhost.run verwendet werden.

   ```
   ssh -R 80:localhost:8000 nokey@localhost.run
   ```
2. **Webhook-Fields konfigurieren**
   Die Webhook-Fields dienen zur Verwaltung der abonnierten Webhooks. Dort kannst du unter dem "messages"-Field testen, ob die Webhook funktioniert, und anschließend ganz rechts das Kreuz setzen, um Nachrichten hier verarbeiten zu können.

### Voraussetzungen

- Aktive Webhook
- Gestartete Flask-Applikation
- Eingestellte `.env`-Datei

Mit diesen Voraussetzungen sollte der Code funktionieren und fundierte Antworten auf Fitness-Fragen geben können.

## Next Steps

Hier eine unsortierte Auflistung der nächsten Schritte:

- Erstellen eines Objekts mit nötigen Informationen, die danach in einer KV-Store gespeichert und abgerufen werden können.
- Implementieren eines Kontexts als Ersatz der Thread-Funktionalität.
- Abrufen des Objekts aus der KV-Store, um Berichte über Nährwerte zu erstellen.
- Festlegen eines festen Konversationsflusses über mehrere Tage hinweg, abhängig vom Datum (aktuelles Datum - Datum der ersten Nachricht).
