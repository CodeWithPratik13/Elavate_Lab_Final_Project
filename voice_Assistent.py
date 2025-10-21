import requests
import json
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser as wb
import os
import random
import pyautogui
import pyjokes
from playsound import playsound
import tempfile

# ===== API Keys =====
GEMINI_API_KEY = "YOUR_API_KEY"
ELEVEN_API_KEY = "YOUR_API_KEY"

# ===== API URLs =====
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
ELEVEN_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# ===== Voice Settings =====
ELEVEN_VOICE_ID = "fPIfC3elMLbN9tNwMXkw"  # You can change to any Eleven voice (e.g. "Adam", "Domi", etc.)

# ---------- ElevenLabs Voice Function ----------
def speak(text):
    """Convert text to speech using ElevenLabs"""
    if not text or text.strip() == "":
        return

    print(f"🗣️ AI: {text}")
    try:
        # Use a temporary audio file for playback
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            output_path = tmpfile.name

        # ElevenLabs API Request
        tts_url = f"{ELEVEN_API_URL}/{ELEVEN_VOICE_ID}"
        headers = {
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",  # supports Hindi/English mix
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.8},
        }

        response = requests.post(tts_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            playsound(output_path)
        else:
            print("⚠️ ElevenLabs API error:", response.text)
    except Exception as e:
        print("⚠️ Speech error:", e)

# ---------- Utility Functions ----------
def time_now():
    speak(f"The time is {datetime.datetime.now().strftime('%I:%M %p')}")

def date_now():
    now = datetime.datetime.now()
    speak(f"Today's date is {now.strftime('%B %d, %Y')}")

def wishme():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good morning! How can I help you?")
    elif hour < 18:
        speak("Good afternoon! What can I do for you?")
    else:
        speak("Good evening! How may I assist you?")
    speak("Your AI assistant is now online and ready to help you.")

def takecommand():
    """Take voice input"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(f"🧠 You said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn’t get that. Could you repeat?")
        return ""
    except sr.RequestError:
        speak("Speech service unavailable.")
        return ""
    except Exception as e:
        print(e)
        speak("An error occurred.")
        return ""

def screenshot():
    img = pyautogui.screenshot()
    path = os.path.expanduser("~\\Pictures\\screenshot.png")
    img.save(path)
    speak(f"Screenshot saved to {path}")

def play_music(song_name=None):
    music_dir = os.path.expanduser("~\\Music")
    songs = os.listdir(music_dir)
    if song_name:
        songs = [s for s in songs if song_name.lower() in s.lower()]
    if songs:
        song = random.choice(songs)
        os.startfile(os.path.join(music_dir, song))
        speak(f"Playing {song}")
    else:
        speak("No matching song found.")

def ai_answer(question):
    """Get AI answer from Gemini"""
    speak("Let me think about that...")
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": question}]}]}
    params = {"key": GEMINI_API_KEY}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            full_answer = result["candidates"][0]["content"]["parts"][0]["text"]
            print("\n🤖 Gemini Answer:\n", full_answer, "\n")
            short_summary = ". ".join(full_answer.split(". ")[:3])
            speak(short_summary)
        else:
            print("❌ Gemini API error:", response.text)
            speak("Sorry, Gemini did not respond correctly.")
    except Exception as e:
        print("❌ Error:", e)
        speak("Sorry, I had trouble connecting to Gemini.")

# ---------- Main Loop ----------
def main():
    wishme()
    while True:
        query = takecommand()
        if not query:
            continue

        if "time" in query:
            time_now()
        elif "date" in query:
            date_now()
        elif "wikipedia" in query:
            speak("Searching Wikipedia...")
            try:
                result = wikipedia.summary(query.replace("wikipedia", ""), sentences=2)
                speak(result)
            except:
                speak("Sorry, I couldn't find that on Wikipedia.")
        elif "open youtube" in query:
            wb.open("https://youtube.com")
            speak("Opening YouTube.")
        elif "open google" in query:
            wb.open("https://google.com")
            speak("Opening Google.")
        elif "screenshot" in query:
            screenshot()
        elif "joke" in query:
            speak(pyjokes.get_joke())
        elif "play music" in query:
            play_music()
        elif "shutdown" in query:
            speak("Shutting down your system.")
            os.system("shutdown /s /t 1")
            break
        elif "restart" in query:
            speak("Restarting your system.")
            os.system("shutdown /r /t 1")
            break
        elif "exit" in query or "offline" in query or "bye" in query:
            speak("Going offline. Have a great day!")
            break
        else:
            ai_answer(query)

if __name__ == "__main__":
    main()
