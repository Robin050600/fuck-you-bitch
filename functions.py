import requests
import json
import os
import random

# API-Schlüssel (sicher speichern!)
PONS_API_KEY = "c9d57f32ea32019e1088ee54c0c38f86daed6d15dc18f6afe0a2fc61698d9332"  # Ersetze mit deinem PONS API-Schlüssel
GROK_API_KEY = "xai-uOzSSJW1PHZZUPqZKznd6fyiaBcGkVAyQEWHacCReXDsEiTcWh4bmjJ47azeD0EvC1KngpXHBBsPDpV6"   # Ersetze mit deinem Grok API-Schlüssel

# PONS API für Wörter und Übersetzungen
def fetch_pons_words(limit=100):
    url = "https://api.pons.com/v1/dictionary"
    headers = {"X-Secret": PONS_API_KEY}
    params = {"language": "en-de", "limit": limit}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json()
            words = []
            for item in results:
                word = item.get("word", "")
                translation = item["translations"][0]["target"] if item.get("translations") else ""
                meaning = item.get("definition", "") or item.get("description", "")
                if word and translation:
                    words.append({"word": word, "translation": translation, "meaning": meaning})
            return words[:limit]
        else:
            print(f"PONS API Fehler: {response.status_code}")
            return []
    except Exception as e:
        print(f"Fehler bei PONS API: {e}")
        # Fallback: Simulierte Liste
        return [
            {"word": "apple", "translation": "Apfel", "meaning": "A fruit that grows on trees."},
            {"word": "car", "translation": "Auto", "meaning": "A vehicle with four wheels."},
            {"word": "banana", "translation": "Banane", "meaning": "A yellow fruit."},
            {"word": "shirt", "translation": "Hemd", "meaning": "A piece of clothing for the upper body."},
            {"word": "bread", "translation": "Brot", "meaning": "A staple food made from flour."}
        ]

# Grok API für Filterung
def ask_grok(theme, words, difficulty):
    difficulty_text = {
        "Beginner": "simple, everyday words that beginners understand, like 'apple' or 'bread'",
        "Intermediate": "moderately complex words, like 'recipe' or 'dessert'",
        "Advanced": "complex or rare words, like 'cuisine' or 'gastronomy'"
    }[difficulty]

    prompt = f"""
    Here is a list of words with meanings:
    {json.dumps(words, indent=2)}
    Select up to 20 {difficulty_text} that relate to the theme '{theme}'. Return only the words as a JSON list, e.g., ["apple", "banana"].
    """

    try:
        response = requests.post(
            "https://api.grok.xai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}"},
            json={
                "model": "grok-beta",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return json.loads(response.json()["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"Fehler bei Grok: {e}")
        return []

# Modul erstellen mit Loop
def create_module(theme, difficulty):
    target_count = 20
    collected_words = []
    used_words = set()
    max_attempts = 5

    while len(collected_words) < target_count and max_attempts > 0:
        new_words = fetch_pons_words(limit=100)
        new_words = [w for w in new_words if w["word"] not in used_words]
        if not new_words:
            break

        filtered_words = ask_grok(theme, new_words, difficulty)
        for word in filtered_words:
            if word not in used_words and len(collected_words) < target_count:
                for w in new_words:
                    if w["word"] == word:
                        collected_words.append({"word": word, "translation": w["translation"]})
                        used_words.add(word)
                        break
        max_attempts -= 1

    if len(collected_words) < target_count:
        print(f"Warnung: Nur {len(collected_words)} Wörter gefunden für {theme} ({difficulty})")

    module = {
        "theme": theme,
        "difficulty": difficulty,
        "words": collected_words
    }
    # Speichern
    modules_file = "data/modules.json"
    os.makedirs("data", exist_ok=True)
    try:
        with open(modules_file, "r") as f:
            existing_modules = json.load(f)
    except:
        existing_modules = []
    existing_modules.append(module)
    with open(modules_file, "w") as f:
        json.dump(existing_modules, f, indent=2)
    return module

# Gespeicherte Module laden
def get_saved_modules():
    modules_file = "data/modules.json"
    try:
        with open(modules_file, "r") as f:
            return json.load(f)
    except:
        return []
