import logging
from flask import current_app, jsonify, Flask
from app.utils.vercel_kv import KV
from app.services.openai_service import progress_rating, make_statistics
import json
import requests
import re
import time

def calculate_total_calories():
    kv = KV()
    # Fetch the stored data
    all_parsed_messages = kv.get("+4917634309888")
    
    if not all_parsed_messages:
        return "Not enough data to calculate total calories."
    
    try:
        data = json.loads(all_parsed_messages)
    except json.JSONDecodeError:
        return "Error decoding stored data."
    
    # Extract required information
    progress = data.get("progress", [])
    if not progress:
        return "Not enough data to calculate total calories."

    latest_entry = progress[-1]  # Get the latest entry
    weight = latest_entry.get("weight")
    height = data.get("height")
    age = latest_entry.get("age")
    gender = data.get("gender")

    if None in [weight, height, age, gender]:
        return "Incomplete data for calorie calculation."

    # Calculate the BMR based on gender
    if gender.lower() == "male":
        bmr = 66.473 + (13.752 * weight) + (5.003 * height) - (6.755 * age)
    elif gender.lower() == "female":
        bmr = 655.096 + (9.563 * weight) + (1.850 * height) - (4.676 * age)

    return bmr-500

def calculate_protein_intake():
    kv = KV()
    # Fetch the stored data
    all_parsed_messages = kv.get("+4917634309888")
    
    if not all_parsed_messages:
        return "Not enough data to calculate protein intake."
    
    try:
        data = json.loads(all_parsed_messages)
    except json.JSONDecodeError:
        return "Error decoding stored data."
    
    # Extract required information
    progress = data.get("progress", [])
    if not progress:
        return "Not enough data to calculate protein intake."

    latest_entry = progress[-1]  # Get the latest entry
    weight = latest_entry.get("weight")
    return weight * 2

def process_progress():
    kv = KV()
    # Fetch the stored data
    all_parsed_messages = kv.get("+4917634309888")
    
    if not all_parsed_messages:
        return "Not enough data to process progress."
    
    try:
        data = json.loads(all_parsed_messages)
    except json.JSONDecodeError:
        return "Error decoding stored data."

    # Extract progress entries
    progress = data.get("progress", [])
    if not progress:
        return "Not enough data to process progress."

    # Concatenate all progress entries into a single string
    progress_str = '\n'.join([json.dumps(entry) for entry in progress])
    
    # Send to process_rating for evaluation
    rating_response = progress_rating(progress_str)
    
    return rating_response

def statistics_from_progress():
    kv = KV()
    # Fetch the stored data
    all_parsed_messages = kv.get("+4917634309888")
    
    if not all_parsed_messages:
        return "Not enough data to calculate statistics."
    
    try:
        data = json.loads(all_parsed_messages)
    except json.JSONDecodeError:
        return "Error decoding stored data."

    # Extract progress entries
    progress = data.get("progress", [])
    if not progress:
        return "Not enough data to calculate statistics."

    # Ensure each entry is a dictionary by parsing if necessary
    parsed_progress = []
    for entry in progress:
        if isinstance(entry, str):
            try:
                entry = json.loads(entry)
            except json.JSONDecodeError:
                continue  # Skip entries that cannot be parsed
        parsed_progress.append(entry)

    # Extract required information
    calories = [entry.get("calories", 0) for entry in parsed_progress if entry.get("calories") is not None]
    steps = [entry.get("steps", 0) for entry in parsed_progress if entry.get("steps") is not None]
    weight = [entry.get("weight", 0) for entry in parsed_progress if entry.get("weight") is not None]
    protein = [entry.get("protein", 0) for entry in parsed_progress if entry.get("protein") is not None]

    # Calculate statistics
    avg_calories = sum(calories) / len(calories) if calories else 0
    avg_steps = sum(steps) / len(steps) if steps else 0
    avg_weight = sum(weight) / len(weight) if weight else 0
    avg_protein = sum(protein) / len(protein) if protein else 0

    data = f"""
        "avg_calories": {avg_calories},
        "avg_steps": {avg_steps},
        "avg_weight": {avg_weight},
        "avg_protein": {avg_protein}
        """
    return make_statistics(data)