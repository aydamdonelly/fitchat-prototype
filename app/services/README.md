## Übersicht der Funktionen

### OpenAI Client Konfiguration

- **OPENAI_API_KEY**: API-Schlüssel für die Authentifizierung bei OpenAI.
- **OPENAI_ASSISTANT_ID**: ID des OpenAI-Assistenten.
- **client**: OpenAI-Client, konfiguriert mit dem API-Schlüssel.
- **model**: ChatOpenAI-Instanz, konfiguriert mit dem API-Schlüssel.

### Parser und Prompt-Template Einrichtung

- **output_parser**: PydanticOutputParser, um die Ausgabe zu parsen.
- **prompt**: PromptTemplate, um die Eingabeaufforderungen zu erstellen.
- **chain**: Verkettung von PromptTemplate, Modell und OutputParser.

### Funktionen

1. **upload_file()**: Lädt eine Datei mit einem bestimmten Zweck hoch.
2. **create_assistant(file)**: Erstellt einen neuen Assistenten mit einer Wissensdatenbank.
3. **classify_message(message)**: Klassifiziert eingehende Nachrichten als "daily" oder "individual".
4. **progress_rating(message)**: Bewertet den Fortschritt des Benutzers und gibt Feedback.
5. **make_statistics(message)**: Erstellt eine statistische Auswertung des Fortschritts des Benutzers.
6. **check_if_thread_exists(wa_id)**: Überprüft, ob ein Thread für eine bestimmte WhatsApp-ID existiert.
7. **parse_message(message)**: Parst eine Nachricht mithilfe der definierten Kette.
8. **store_thread(wa_id, thread_id)**: Speichert einen Thread in einer Shelve-Datenbank.
9. **run_assistant(thread, name)**: Führt den Assistenten aus und wartet auf die Fertigstellung.
10. **generate_response(message_body, wa_id, name)**: Generiert eine Antwort auf eine eingehende Nachricht.

## Detaillierte Beschreibung der Funktionen

### upload_file

Lädt eine Datei hoch, die als Wissensbasis für den Assistenten dient.

```python
def upload_file():
    file = client.files.create(
        file=open("../../data/diet.pdf", "rb"), purpose="assistants"
    )
    return file
```

### create_assistant

Erstellt einen neuen Assistenten, der auf die hochgeladene Datei zugreifen kann.

```python
def create_assistant(file):
    assistant = client.beta.assistants.create(
        name="FitChat",
        instructions="You're a helpful WhatsApp assistant that assists users in their mission to lose weight and to keep track of their calories and steps throughout the day...",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview",
        file_ids=[file.id],
    )
    return assistant
```

### classify_message

Klassifiziert eine eingehende Nachricht als "daily" oder "individual".

```python
def classify_message(message):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an intelligent assistant..."},
        {"role": "user", "content": f'... Here is the message you have to classify: {message}'}
    ],
    max_tokens=10,
    temperature=0.9)
    generated_prompt = response.choices[0].message.content.strip()
    return generated_prompt
```

### progress_rating

Bewertet den Fortschritt des Benutzers und gibt Feedback.

```python
def progress_rating(message):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an intelligent assistant..."},
        {"role": "user", "content": f'... give him an evaluation of their progress: {message}'}
    ],
    max_tokens=200,
    temperature=0.9)
    generated_prompt = response.choices[0].message.content.strip()
    return generated_prompt
```

### make_statistics

Erstellt eine statistische Auswertung des Fortschritts des Benutzers.

```python
def make_statistics(message):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an intelligent assistant..."},
        {"role": "user", "content": f'... give him an evaluation of their progress: {message}'}
    ],
    max_tokens=200,
    temperature=0.9)
    generated_prompt = response.choices[0].message.content.strip()
    return generated_prompt
```

### check_if_thread_exists

Überprüft, ob ein Thread für eine bestimmte WhatsApp-ID existiert.

```python
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)
```

### parse_message

Parst eine Nachricht mithilfe der definierten Kette.

```python
def parse_message(message):
    parsed_message = chain.invoke({"query": message})
    return parsed_message
```

### store_thread

Speichert einen Thread in einer Shelve-Datenbank.

```python
def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id
```

### run_assistant

Führt den Assistenten aus und wartet auf die Fertigstellung.

```python
def run_assistant(thread, name):
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    logging.info(f"Generated message: {new_message}")
    return new_message
```

### generate_response

Generiert eine Antwort auf eine eingehende Nachricht.

```python
def generate_response(message_body, wa_id, name):
    thread_id = check_if_thread_exists(wa_id)
    if thread_id is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id
    else:
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )
    new_message = run_assistant(thread, name)
    return new_message
```

## Verwendung

1. **Umgebungsvariablen einrichten**:
   - Erstellen Sie eine `.env`-Datei im Projektverzeichnis.
   - Fügen Sie die erforderlichen Umgebungsvariablen hinzu (`OPENAI_API_KEY`, `OPENAI_ASSISTANT_ID`).

2. **Funktionen aufrufen**:
   - Verwenden Sie die oben beschriebenen Funktionen, um Nachrichten zu klassifizieren, zu parsen, Fortschritte zu bewerten und Antworten zu generieren.

Diese Datei integriert OpenAI-APIs, um eine intelligente und interaktive Kommunikation für Fit Chat bereitzustellen.
