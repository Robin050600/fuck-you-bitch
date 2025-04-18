import json
import os
import random

# Fallback-Daten für Tests
def fetch_pons_words(limit=100):
    return [
        {"word": "apple", "translation": "Apfel", "meaning": "A fruit that grows on trees."},
        {"word": "banana", "translation": "Banane", "meaning": "A yellow fruit."},
        {"word": "bread", "translation": "Brot", "meaning": "A staple food made from flour."},
        {"word": "cheese", "translation": "Käse", "meaning": "A dairy product."},
        {"word": "shirt", "translation": "Hemd", "meaning": "A piece of clothing."},
        {"word": "jacket", "translation": "Jacke", "meaning": "A piece of outerwear."},
        {"word": "car", "translation": "Auto", "meaning": "A vehicle with four wheels."},
        {"word": "train", "translation": "Zug", "meaning": "A mode of transport."},
        {"word": "milk", "translation": "Milch", "meaning": "A dairy drink."},
        {"word": "pants", "translation": "Hose", "meaning": "Clothing for legs."},
        {"word": "bus", "translation": "Bus", "meaning": "A public transport vehicle."}
    ]

# Einfache Filterung statt Grok-API
def ask_grok(theme, words, difficulty):
    theme_words = {
        "Essen": ["apple", "banana", "bread", "cheese", "milk"],
        "Kleidung": ["shirt", "jacket", "pants"],
        "Reisen": ["car", "train", "bus"]
    }
    filtered = [w for w in theme_words.get(theme, []) if w in [word["word"] for word in words]]
    return filtered, f"Filterung für Thema: {theme}, Schwierigkeitsgrad: {difficulty}, Gefilterte Wörter: {filtered}"

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
