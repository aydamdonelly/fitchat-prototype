import logging
from flask import current_app, jsonify, Flask
import json
import requests
import re
import schedule
import time
from app.services.openai_service import generate_response, classify_message

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")

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
    with app.app_context():
        data = get_text_message_input(current_app.config["RECIPIENT_WAID"], "How many steps have you walked today? And how many calories have you consumed?")
        send_message(data)

def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config["VERSION"]}/{current_app.config["PHONE_NUMBER_ID"]}/messages"

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

    # TODO: implement custom function here
    # response = generate_response(message_body)

    classification = classify_message(message_body)

    # OpenAI Integration
    if classification != "daily":
        response = generate_response(message_body, wa_id, name)
        response = process_text_for_whatsapp(response)
    elif classification == "daily":
        recipient = current_app.config["RECIPIENT_WAID"]
        message_id = message["id"]
        reaction_emoji = "\u270D"

        url = f"https://graph.facebook.com/{current_app.config["VERSION"]}/{current_app.config["PHONE_NUMBER_ID"]}/messages"
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

        # Log the reaction response
        print(reaction_response.status_code)
        print(reaction_response.json())

    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
    send_message(data)

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

# Aufgabenplanung konfigurieren
def schedule_tasks(app: Flask):
    schedule.every(1).minutes.do(send_automated_message, app=app)
