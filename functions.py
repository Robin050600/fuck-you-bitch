import requests
import json
import os
import random

# API-Schlüssel
GROK_API_KEY = "xai-uOzSSJW1PHZZUPqZKznd6fyiaBcGkVAyQEWHacCReXDsEiTcWh4bmjJ47azeD0EvC1KngpXHBBsPDpV6"

# Fallback-Daten für Tests
def fetch_pons_words(limit=100):
    return [
        {"word": "apple", "translation": "Apfel", "meaning": "A fruit that grows on trees."},
        {"word": "banana", "translation": "Banane", "meaning": "A yellow fruit."},
        {"word": "bread", "translation": "Brot", "meaning": "A staple food made from flour."},
        {"word": "cheese", "translation": "Käse", "meaning": "A dairy product."},
        {"word": "milk", "translation": "Milch", "meaning": "A dairy drink."},
        {"word": "egg", "translation": "Ei", "meaning": "A food from chickens."},
        {"word": "rice", "translation": "Reis", "meaning": "A staple grain."},
        {"word": "meat", "translation": "Fleisch", "meaning": "Animal flesh used as food."},
        {"word": "fish", "translation": "Fisch", "meaning": "A sea creature used as food."},
        {"word": "shirt", "translation": "Hemd", "meaning": "A piece of clothing."},
        {"word": "jacket", "translation": "Jacke", "meaning": "A piece of outerwear."},
        {"word": "pants", "translation": "Hose", "meaning": "Clothing for legs."},
        {"word": "shoes", "translation": "Schuhe", "meaning": "Footwear."},
        {"word": "hat", "translation": "Hut", "meaning": "Headwear."},
        {"word": "car", "translation": "Auto", "meaning": "A vehicle with four wheels."},
        {"word": "train", "translation": "Zug", "meaning": "A mode of transport."},
        {"word": "bus", "translation": "Bus", "meaning": "A public transport vehicle."},
        {"word": "airplane", "translation": "Flugzeug", "meaning": "A flying vehicle."},
        {"word": "bicycle", "translation": "Fahrrad", "meaning": "A two-wheeled vehicle."}
    ]

# Grok API für Filterung
def ask_grok(theme, words, difficulty):
    debug_log = f"Filterung für Thema: {theme}, Schwierigkeitsgrad: {difficulty}"
    
    # Schwierigkeitsgrad-Definition
    difficulty_text = {
        "Beginner": "simple, everyday words that beginners understand, like 'apple' or 'bread'",
        "Intermediate": "moderately complex words, like 'recipe' or 'dessert'",
        "Advanced": "complex or rare words, like 'cuisine' or 'gastronomy'"
    }[difficulty]

    # Prompt für Grok
    prompt = f"""
    You are a language learning assistant. Given a list of words with their meanings, select up to 20 words that relate to the theme '{theme}' and match the difficulty level '{difficulty_text}'. Return only the words as a JSON list, e.g., ["apple", "banana"]. If no words match, return an empty list [].

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
        debug_log += f", HTTP-Status: {response.status_code}"
        if response.status_code == 200:
            try:
                result = json.loads(response.json()["choices"][0]["message"]["content"])
                if not isinstance(result, list):
                    debug_log += f", API-Antwort ist kein JSON-Array: {result}"
                    raise ValueError("API-Antwort ist kein JSON-Array")
                debug_log += f", Gefilterte Wörter: {result}"
                return result, debug_log
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                debug_log += f", Fehler beim Parsen der API-Antwort: {str(e)}"
                raise
        else:
            debug_log += f", Grok API Fehler: Status {response.status_code}, Antwort: {response.text}"
            raise Exception(f"HTTP-Fehler: {response.status_code}")
    except Exception as e:
        debug_log += f", Fehler bei Grok API: {str(e)}"
        # Fallback: Einfache Filterung
        theme_words = {
            "Essen": ["apple", "banana", "bread", "cheese", "milk", "egg", "rice", "meat", "fish"],
            "Kleidung": ["shirt", "jacket", "pants", "shoes", "hat"],
            "Reisen": ["car", "train", "bus", "airplane", "bicycle"]
        }
        filtered = [w for w in theme_words.get(theme, []) if w in [word["word"] for word in words]]
        debug_log += f", Fallback aktiviert, Gefilterte Wörter: {filtered}"
        return filtered, debug_log

# Modul erstellen
def create_module(theme, difficulty):
    debug_logs = []
    debug_logs.append("Starte Modulerstellung")
    target_count = 20
    collected_words = []
    used_words = set()
    max_attempts = 5

    while len(collected_words) < target_count and max_attempts > 0:
        new_words = fetch_pons_words(limit=100)
        debug_logs.append(f"Neue Wörter geladen: {len(new_words)} verfügbar")
        new_words = [w for w in new_words if w["word"] not in used_words]
        debug_logs.append(f"Nach Entfernen verwendeter Wörter: {len(new_words)} verfügbar")
        if not new_words:
            debug_logs.append("Keine neuen Wörter verfügbar, Schleife abgebrochen")
            break

        filtered_words, filter_log = ask_grok(theme, new_words, difficulty)
        debug_logs.append(filter_log)
        for word in filtered_words:
            if word not in used_words and len(collected_words) < target_count:
                for w in new_words:
                    if w["word"] == word:
                        collected_words.append({"word": word, "translation": w["translation"]})
                        used_words.add(word)
                        debug_logs.append(f"Wort hinzugefügt: {word}")
                        break
        max_attempts -= 1
        debug_logs.append(f"Versuch {6 - max_attempts}: {len(collected_words)} Wörter gesammelt")

    if len(collected_words) < target_count:
        debug_logs.append(f"Warnung: Nur {len(collected_words)} Wörter gefunden für {theme} ({difficulty})")
    else:
        debug_logs.append(f"Erfolg: {len(collected_words)} Wörter für {theme} ({difficulty})")

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
    try:
        with open(modules_file, "w") as f:
            json.dump(existing_modules, f, indent=2)
        debug_logs.append("Modul erfolgreich in modules.json gespeichert")
    except Exception as e:
        debug_logs.append(f"Fehler beim Speichern von modules.json: {str(e)}")

    return module, debug_logs

# Gespeicherte Module laden
def get_saved_modules():
    modules_file = "data/modules.json"
    try:
        with open(modules_file, "r") as f:
            return json.load(f)
    except:
        return []
