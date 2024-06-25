import logging
from flask import current_app, jsonify, Flask
from app.utils.vercel_kv import KV
import json
import requests
import re
import schedule
import time
from app.utils.special_events import calculate_total_calories, calculate_protein_intake, process_progress, statistics_from_progress
from app.services.openai_service import generate_response, classify_message, parse_message

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")

kv = KV()

def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

def send_automated_message(app: Flask):
    questions = [
        lambda: "Hey there! I'm Fit Chat! My goal is to help you in your fitness and health journey and to help you lose weight. For this to work, I recommend enabling the built-in step-tracker in your device. Let's get started! How many steps did you walk today? And also, what gender are you? Last but not least, I'd like to know your age. I'll be asking you every day from now on, promise :). If you have any questions, don't hesitate to ask me!",
        lambda: "Hi! In order to lose weight, it's also important to take the current weight into account. Because of that, I need to know your current weight. Like yesterday, I'd also like to know how many steps you've walked. See you tomorrow!",
        lambda: "Hello! Working with proteins is important in the journey of losing weight. There are various platforms which help you track those. I recommend YAZIO! How many grams of protein and how many calories have you consumed today? And also, how many steps have you walked today and how much do you weigh? See you tomorrow!",
        lambda: f"""Hey there! I have something for you! Based on your information, I've created a plan on how you lose weight the best way! Don't forget to inform me with your weight, step count and protein intake! Here's your plan:

        Daily Protein Intake: {calculate_protein_intake()} grams.
        Daily Calorie Intake: {calculate_total_calories()} calories.
        Daily Steps: 10000 to 15000 steps.
        Strength training (3x/week, Bench press, Back squats, Deadlifts, Pull-ups).
        Cardio (1-2x/week, 30 minutes).
        Sleep: 6-8 hours, aim for 8 hours.
        """,
        lambda: "Hey there! Please provide me with the following info: Weight, steps, protein intake and calories. Thank you! See you tomorrow!",
        lambda: f"{process_progress()}. Make sure to provide me with the following information: weight, steps, protein intake and calories. Thank you! See you tomorrow!",
        lambda: "Hello! Could you please provide me with your weight, steps walked, protein intake, and calorie count? Thank you! See you tomorrow!",
        lambda: f"{statistics_from_progress()}. \n \nAnd don't forget to provide me with your weight, steps, protein intake, and calorie count. Thank you! See you tomorrow!",
        lambda: "Hi! Please provide me with your weight, steps walked, protein intake and calorie count. Thanks!",
        lambda: "Hi! Please provide me with your weight, steps walked, protein intake and calorie count. Thanks!",
        lambda: "Hi! Please provide me with your weight, steps walked, protein intake and calorie count. Thanks!",
        lambda: "Hi! Please provide me with your weight, steps walked, protein intake and calorie count. Thanks!",
        lambda: "Hi! Please provide me with your weight, steps walked, protein intake and calorie count. Thanks!",
        lambda: "Hi! Please provide me with your weight, steps walked, protein intake and calorie count. Thanks!",
        lambda: "Hi! Please provide me with your weight, steps walked, protein intake and calorie count. Thanks!",
        lambda: "Hey there! Your trial period ended. For the service to continue, please pay through this link: https://www.paypal.com/paypalme/fitchat. Thank you!",
    ]
    
    with app.app_context():
        # Abrufen der JSON-Nachricht aus dem KV-Store
        all_parsed_messages = kv.get("+4917634309888")
        
        if not all_parsed_messages:
            all_parsed_messages = {
                "progress": [],
                "current_day": 1
            }
        else:
            try:
                all_parsed_messages = json.loads(all_parsed_messages)
            except json.JSONDecodeError:
                all_parsed_messages = {
                    "progress": [],
                    "current_day": 1
                }
        
        # Anzahl der progress-Einträge zählen
        progress_count = len(all_parsed_messages["progress"])
        
        # Eine Frage basierend auf der Anzahl der progress-Einträge auswählen
        question_func = questions[progress_count % len(questions)]
        question = question_func()  # Call the function to get the actual question text
        
        # Nachrichtendaten vorbereiten
        data = get_text_message_input(current_app.config["RECIPIENT_WAID"], question)
        
        # Nachricht senden
        send_message(data)

def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response

def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text

def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    if message_body == "Reset":
        kv.set("+4917634309888", "")

    # TODO: implement custom function here
    # response = generate_response(message_body)

    classification = classify_message(message_body)

    # OpenAI Integration
    if classification != "daily":
        response = generate_response(message_body, wa_id, name)
        response = process_text_for_whatsapp(response)
        data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
        send_message(data)
    elif classification == "daily":
        recipient = current_app.config["RECIPIENT_WAID"]
        message_id = message["id"]
        reaction_emoji = "\u270D"

        url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {current_app.config['ACCESS_TOKEN']}"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": current_app.config["RECIPIENT_WAID"],
            "type": "reaction",
            "reaction": {
                "message_id": message_id,
                "emoji": reaction_emoji
            }
        }

        reaction_response = requests.post(url, headers=headers, data=json.dumps(payload))

        parsed_message = convert_to_json(str(parse_message(message_body)))

        all_parsed_messages = kv.get("+4917634309888")

        if not all_parsed_messages:
            all_parsed_messages = {
                "progress": [],
                "current_day": 1,
                "height": None,
                "gender": None,
            }
        else:
            try:
                # Versuch, den JSON-String zu dekodieren
                all_parsed_messages = json.loads(all_parsed_messages)
            except json.JSONDecodeError:
                # Fehlerbehandlung, falls das Dekodieren fehlschlägt
                all_parsed_messages = {
                    "progress": [],
                    "current_day": 1,
                    "height": None,
                    "gender": None,
                }

        # Update the height and gender if they are present in parsed_message
        if 'height' in parsed_message:
            all_parsed_messages['height'] = parsed_message.pop('height')
        if 'gender' in parsed_message:
            all_parsed_messages['gender'] = parsed_message.pop('gender')
        if 'age' in parsed_message:
            all_parsed_messages['age'] = parsed_message.pop('age')

        all_parsed_messages["progress"].append(parsed_message)
        all_parsed_messages["current_day"] += 1

        #json.dumps is used to convert the dictionary to a string
        kv.set("+4917634309888", json.dumps(all_parsed_messages))

        # Log the reaction response
        print(reaction_response.status_code)
        print(reaction_response.json())

def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

def convert_to_json(parsed_metrics):
    data_dict = {}
    for item in parsed_metrics.split():
        key, value = item.split('=')
        if value == 'None':
            value = None
        elif value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass
        data_dict[key] = value
    return data_dict

# Aufgabenplanung konfigurieren
def schedule_tasks(app: Flask):
    schedule.every(1).minutes.do(send_automated_message, app=app)
