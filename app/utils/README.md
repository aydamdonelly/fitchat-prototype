## Struktur der utils

Das Projekt besteht aus mehreren Python-Dateien, die zusammenarbeiten, um die Funktionalität von Fit Chat bereitzustellen:

1. **special_events.py**
2. **whatsapp_utils.py**
3. **vercel_kv.py**

### 1. special_events.py

Diese Datei enthält Funktionen zur Berechnung und Verarbeitung von Fitnessdaten.

- **calculate_total_calories**: Berechnet die Gesamtzahl der zu verbrauchenden Kalorien basierend auf den Benutzerdaten (Geschlecht, Gewicht, Größe, Alter).
- **calculate_protein_intake**: Berechnet die tägliche Proteinaufnahme basierend auf dem Gewicht des Benutzers.
- **process_progress**: Verarbeitet die Fortschrittsdaten des Benutzers und sendet diese zur Bewertung an die `progress_rating`-Funktion.
- **statistics_from_progress**: Berechnet statistische Daten aus dem Fortschritt des Benutzers (Durchschnittswerte für Kalorien, Schritte, Gewicht und Protein).

### 2. whatsapp_utils.py

Diese Datei enthält Funktionen zur Verwaltung und Verarbeitung von WhatsApp-Nachrichten.

- **log_http_response**: Protokolliert HTTP-Antworten.
- **get_text_message_input**: Erstellt JSON-Nachrichten für WhatsApp.
- **send_automated_message**: Sendet automatisierte Nachrichten an den Benutzer basierend auf dem Fortschritt und den vordefinierten Fragen.
- **send_message**: Sendet Nachrichten über die WhatsApp-API.
- **process_text_for_whatsapp**: Formatiert Text für WhatsApp, indem spezielle Zeichen ersetzt werden.
- **process_whatsapp_message**: Verarbeitet eingehende WhatsApp-Nachrichten, klassifiziert sie und speichert die relevanten Daten im KV-Store.
- **is_valid_whatsapp_message**: Überprüft die Struktur eingehender WhatsApp-Nachrichten.
- **convert_to_json**: Konvertiert geparste Metriken in JSON-Format.
- **schedule_tasks**: Plant Aufgaben zur automatischen Nachrichtenübermittlung.

### 3. vercel_kv.py

Diese Datei enthält eine Wrapper-Klasse für die Vercel KV-API, die zum Speichern und Abrufen von Daten verwendet wird.

- **KVConfig**: Modelliert die Konfiguration für den KV-Store.
- **Opts**: Modelliert optionale Parameter für die KV-Store-Operationen.
- **KV**: Enthält Methoden zum Setzen und Abrufen von Daten im KV-Store.

## Kommunikation zwischen den Dateien

Die Kommunikation zwischen den Dateien erfolgt hauptsächlich über Funktionsaufrufe und das Speichern/Abrufen von Daten im Vercel KV-Store.

- **special_events.py** ruft Funktionen auf, um Kalorien, Proteinaufnahme und Fortschrittsdaten zu berechnen und zu verarbeiten. Es verwendet den KV-Store, um Benutzerdaten abzurufen.
- **whatsapp_utils.py** verwaltet die Interaktion mit der WhatsApp-API. Es verwendet die in **special_events.py** definierten Funktionen, um die täglichen Nachrichten basierend auf den berechneten Fitnessdaten zu generieren.
- **vercel_kv.py** stellt die Schnittstelle zum Vercel KV-Store bereit, die von beiden anderen Dateien genutzt wird, um Benutzerdaten zu speichern und abzurufen.
