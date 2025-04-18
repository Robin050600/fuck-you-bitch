import streamlit as st
from functions import create_module, get_saved_modules

# CSS für einfache UI
st.markdown("""
<style>
body { background-color: #f0f2f6; }
.stButton>button { background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px; }
.card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; }
.feedback { font-size: 18px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# Session State
if "module" not in st.session_state:
    st.session_state.module = None
    st.session_state.current_word_index = 0
    st.session_state.feedback = ""

# Sidebar
st.sidebar.title("Sprachlern-App")
mode = st.sidebar.selectbox("Modus", ["Modul erstellen", "Übersetzungen üben", "Grok-API testen"])

# Hauptbereich
if mode == "Modul erstellen":
    st.header("Modul erstellen")
    theme = st.selectbox("Thema", ["Essen", "Kleidung", "Reisen"])
    difficulty = st.selectbox("Schwierigkeitsgrad", ["Beginner", "Intermediate", "Advanced"])
    if st.button("Modul erstellen"):
        try:
            st.session_state.module, debug_logs = create_module(theme, difficulty)
            st.session_state.current_word_index = 0
            st.session_state.feedback = ""
            st.success(f"Modul für {theme} ({difficulty}) erstellt!")
            st.write("Debug: Modulinhalt:", st.session_state.module)
            if st.session_state.module["words"]:
                st.write("Wörter:", [w["word"] for w in st.session_state.module["words"]])
            else:
                st.error("Keine Wörter im Modul! Siehe Debug-Logs unten.")
            st.subheader("Debug-Logs:")
            for log in debug_logs:
                st.write(log)
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Moduls: {e}")

elif mode == "Übersetzungen üben":
    st.header("Übersetzungen üben")
    saved_modules = get_saved_modules()
    if not saved_modules:
        st.error("Keine Module vorhanden! Erstelle zuerst ein Modul.")
    else:
        module_options = [f"{m['theme']} ({m['difficulty']})" for m in saved_modules]
        selected_module = st.selectbox("Wähle ein Modul", module_options)
        selected_index = module_options.index(selected_module)
        st.session_state.module = saved_modules[selected_index]

        if st.session_state.module and st.session_state.current_word_index < len(st.session_state.module["words"]):
            word = st.session_state.module["words"][st.session_state.current_word_index]
            st.markdown(f"<div class='card'><h3>{word['word']}</h3></div>", unsafe_allow_html=True)
            user_translation = st.text_input("Gib die Übersetzung ein", key=f"input_{st.session_state.current_word_index}")
            if st.button("Prüfen"):
                correct_translation = word["translation"]
                if user_translation.lower() == correct_translation.lower():
                    st.session_state.feedback = "Richtig! 🎉"
                    st.session_state.current_word_index += 1
                else:
                    st.session_state.feedback = f"Falsch! Richtig ist: {correct_translation}"
            st.markdown(f"<div class='feedback'>{st.session_state.feedback}</div>", unsafe_allow_html=True)
        else:
            st.write("Alle Wörter durch! Wähle ein neues Modul.")

elif mode == "Grok-API testen":
    st.header("Grok-API Test")
    if st.button("API testen"):
        try:
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {GROK_API_KEY}"
                },
                json={
                    "messages": [
                        {"role": "system", "content": "You are a test assistant."},
                        {"role": "user", "content": "Testing. Just say hi and hello world and nothing else."}
                    ],
                    "model": "grok-3-latest",
                    "stream": False,
                    "temperature": 0
                }
            )
            st.write(f"HTTP-Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                st.write("API-Antwort:", result["choices"][0]["message"]["content"])
            else:
                st.error(f"API-Fehler: Status {response.status_code}, Antwort: {response.text}")
        except Exception as e:
            st.error(f"Fehler beim API-Test: {str(e)}")
