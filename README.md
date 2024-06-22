Okay, ich schick dir nach der Nachricht eine Repo mit meinen Inhalten bisher, kurzer Breakdown von dem was ich gemacht habe:

- alles eingerichtet bekommen, das Problem mit ngrok hat mich auch gut Zeit gekostet und ich bin mir ziemlich sicher, dass das Problem daran lag, dass die GET-Request die in der Repo vom Video definiert wurde, gar nicht ausgeführt werden konnte, da ngrok-Links von Meta als potentially malicious eingestuft werden und deswegen ein Zwischenschritt der Verifizierung durchgeführt werden muss, welcher über das Dashboard von Meta for Developers eben nicht umgangen werden kann. Aus dem Grund habe ich Serveo verwendet um das Ganze zu Testen, am Ende landet das ja sowieso soweit ich verstanden habe auf Vercel
- Einen openai-Assistant mit PDF zu passenden Themen erstellt und gefüttert. Wahrscheinlich kennst du das schon, aber openai bietet an, assistants zu erstellen und in diesen Assistants Threads zu führen. Diese Threads dienen für uns individuell je nach Nutzer als Kontext und können in einem Datensatz zusammen mit Thread-ID Informationen wie "Tag" (für den Conversation flow aus dem google doc) oder "Schrittanzahl" (nach Tag) beinhalten.
- Verbinden der WhatsApp API mit OpenAI bzw. dem Assistant, so bekommst du also antworten zu Fragen ggf. basierend auf der PDF als wissensbasis
- regelmäßiges Abfragen der Schritte und Kalorien, das ist erstmal festgesetzter Text, ich plane da noch chatgpt zu verwenden, um die nachrichten ein wenig individuell zu machen und ggf. in den Kontext passen zu lassen, um's zu testen hab ich den Intervall erstmal auf 1 Minute gesetzt (whatsapp_utils.py unter app/utils)

Was die nächsten Schritte wären:
- Informationen pro Nutzer speichern (wie viele Schritte hat er getätigt, usw.)
- Routine-Nachrichten (die in einem festen Zeitintervall, also bspw. jeden Abend versendet werden wie der Vorschlag mit Yazio-Download) festlegen
- Prompt-Tunen, Nachrichten sind oft zu lang
- Handling von mehreren Nachrichten eines Users, die eigentlich eine Anfrage an das LLM darstellen sollen

Offene Fragen:
- benutzen wir OpenAI bzw. deren Assistant-Funktion, um bspw. RAG-Funktionalität einzubauen? Interessant dazu vielleicht das Video: https://www.youtube.com/watch?v=0h1ry-SqINc&t=1142s
