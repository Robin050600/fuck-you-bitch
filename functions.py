import requests
import json
import os
import random

# API-Schlüssel
GROK_API_KEY = "xai-uOzSSJW1PHZZUPqZKznd6fyiaBcGkVAyQEWHacCReXDsEiTcWh4bmjJ47azeD0EvC1KngpXHBBsPDpV6"
PONS_API_KEY = "c9d57f32ea32019e1088ee54c0c38f86daed6d15dc18f6afe0a2fc61698d9332"

# PONS API oder Fallback-Daten
def fetch_pons_words(theme, limit=100):
    # Generischer Suchbegriff basierend auf Thema
    theme_queries = {
        "Essen": "food",
        "Kleidung": "clothing",
        "Reisen": "travel"
    }
    query = theme_queries.get(theme, "word")  # Fallback-Suchbegriff

    try:
        response = requests.get(
            "https://api.pons.com/v1/dictionary",
            headers={"X-Secret": PONS_API_KEY},
            params={"q": query, "l": "ende", "language": "en", "limit": limit}
        )
        debug_log = f"PONS API: Status {response.status_code}, Anfrage: q={query}, l=ende"
        if response.status_code == 200:
            words = []
            for item in response.json():
                if item.get("hits") and item["hits"][0].get("roms"):
                    word_data = item["hits"][0]["roms"][0]
                    translations = word_data.get("arabs", [{}])[0].get("translations", [])
                    if translations:
                        words.append({
                            "word": word_data["headword"],
                            "translation": translations[0]["target"],
                            "meaning": translations[0].get("source", "")
                        })
            debug_log += f", {len(words)} Wörter geladen"
            return words, debug_log
        else:
            debug_log += f", Fehler: {response.text}"
            raise Exception(f"PONS API Fehler: Status {response.status_code}, Antwort: {response.text}")
    except Exception as e:
        debug_log = f"PONS API Fehler: {str(e)}, Fallback aktiviert"
        # Fallback-Daten
        fallback_words = [
            {"word": "apple", "translation": "Apfel", "meaning": "A fruit that grows on trees."},
            {"word": "banana", "translation": "Banane", "meaning": "A yellow fruit."},
            {"word": "bread", "translation": "Brot", "meaning": "A staple food made from flour."},
            {"word": "cheese", "translation": "Käse", "meaning": "A dairy product."},
            {"word": "milk", "translation": "Milch", "meaning": "A dairy drink."},
            {"word": "egg", "translation": "Ei", "meaning": "A food from chickens."},
            {"word": "rice", "translation": "Reis", "meaning": "A staple grain."},
            {"word": "meat", "translation": "Fleisch", "meaning": "Animal flesh used as food."},
            {"word": "fish", "translation": "Fisch", "meaning": "A sea creature used as food."},
            {"word": "pasta", "translation": "Nudeln", "meaning": "A food made from dough."},
            {"word": "soup", "translation": "Suppe", "meaning": "A liquid dish."},
            {"word": "salad", "translation": "Salat", "meaning": "A dish of raw vegetables."},
            {"word": "cake", "translation": "Kuchen", "meaning": "A sweet dessert."},
            {"word": "shirt", "translation": "Hemd", "meaning": "A piece of clothing."},
            {"word": "jacket", "translation": "Jacke", "meaning": "A piece of outerwear."},
            {"word": "pants", "translation": "Hose", "meaning": "Clothing for legs."},
            {"word": "shoes", "translation": "Schuhe", "meaning": "Footwear."},
            {"word": "hat", "translation": "Hut", "meaning": "Headwear."},
            {"word": "scarf", "translation": "Schal", "meaning": "A piece of clothing for the neck."},
            {"word": "gloves", "translation": "Handschuhe", "meaning": "Clothing for hands."},
            {"word": "car", "translation": "Auto", "meaning": "A vehicle with four wheels."},
            {"word": "train", "translation": "Zug", "meaning": "A mode of transport."},
            {"word": "bus", "translation": "Bus", "meaning": "A public transport vehicle."},
            {"word": "airplane", "translation": "Flugzeug", "meaning": "A flying vehicle."},
            {"word": "bicycle", "translation": "Fahrrad", "meaning": "A two-wheeled vehicle."},
            {"word": "boat", "translation": "Boot", "meaning": "A water vehicle."}
        ]
        return fallback_words, debug_log

# Grok API für Filterung
def ask_grok(theme, words, difficulty):
    debug_log = f"Filterung für Thema: {theme}, Schwierigkeitsgrad: {difficulty}"
    
    # Schwierigkeitsgrad-Definition
    difficulty_text = {
        "Beginner": "simple, everyday words suitable for beginners, e.g., 'apple', 'bread'",
        "Intermediate": "moderately complex words suitable for intermediate learners, e.g., 'recipe', 'dessert'",
        "Advanced": "complex or specialized words suitable for advanced learners, e.g., 'cuisine', 'gastronomy'"
    }[difficulty]

    # Prompt für Grok
    prompt = f"""
    You are a language learning assistant. Given a list of words with their meanings, select up to 20 words that relate to the theme '{theme}' and match the difficulty level '{difficulty_text}'. Only select words that are present in the provided list. Return the selected words as a JSON list, e.g., ["apple", "banana"]. If no words match the theme and difficulty, return an empty list [].

    Word list:
    {json.dumps(words, indent=2)}
    """

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROK_API_KEY}"
            },
            json={
                "messages": [
                    {"role": "system", "content": "You are a precise language learning assistant."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok-3-latest",
                "stream": False,
                "temperature": 0
            }
        )
        debug_log += f",
