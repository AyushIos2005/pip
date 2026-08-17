"""
Dora - Voice Assistant (Google Assistant style)
------------------------------------------------
Key "Assistant-like" behaviors this version adds:
  * Wake word ("hey dora" / "ok dora"), then a FOLLOW-UP WINDOW —
    after answering, it keeps listening for a few seconds so you can
    ask another thing without repeating the wake word (just like
    "Ok Google... what about tomorrow?").
  * Varied, natural-sounding responses instead of the same line every time.
  * Timers & reminders that fire in the background while you keep using it.
  * A calculator / quick-math command.
  * Small talk: coin flip, dice roll, spelling, fun facts.

Install:
    pip install pyttsx3 SpeechRecognition pyjokes wikipedia pyaudio requests
"""

import datetime
import random
import re
import threading
import time
import webbrowser

import pyttsx3
import speech_recognition as sr
import pyjokes

try:
    import wikipedia
    HAS_WIKI = True
except ImportError:
    HAS_WIKI = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

WAKE_WORDS = ("hey dora", "ok dora", "okay dora")
EXIT_WORDS = ("exit", "stop listening", "goodbye", "shut down")
VOICE_INDEX = 1
SPEECH_RATE = 170
FOLLOW_UP_SECONDS = 6          # how long it keeps listening after answering, no wake word needed
WEATHER_API_KEY = ""           # optional OpenWeatherMap key


# ---------------------------------------------------------------------------
# Core speech I/O
# ---------------------------------------------------------------------------

_recognizer = sr.Recognizer()
_engine = pyttsx3.init()


def _configure_engine():
    voices = _engine.getProperty('voices')
    if len(voices) > VOICE_INDEX:
        _engine.setProperty('voice', voices[VOICE_INDEX].id)
    _engine.setProperty('rate', SPEECH_RATE)


_configure_engine()


def speak(text: str):
    print(f"Dora: {text}")
    _engine.say(text)
    _engine.runAndWait()


def listen(timeout=5, phrase_time_limit=8) -> str:
    """Listen once, return lowercase text or '' on silence/error."""
    with sr.Microphone() as source:
        _recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = _recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""
    try:
        text = _recognizer.recognize_google(audio)
        print(f"You: {text}")
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        print("Speech service unavailable (check internet).")
        return ""


def say_variant(*options):
    """Speak a randomly chosen phrasing so responses don't feel robotic/repetitive."""
    speak(random.choice(options))


# ---------------------------------------------------------------------------
# Background timers & reminders (fire independently of the listen loop)
# ---------------------------------------------------------------------------

def _fire_timer(label: str):
    speak(f"Time's up on your {label}." if label else "Your timer is done.")


def set_timer(seconds: int, label: str = ""):
    t = threading.Timer(seconds, _fire_timer, args=(label,))
    t.daemon = True
    t.start()


def _fire_reminder(text: str):
    speak(f"Reminder: {text}")


def set_reminder(seconds: int, text: str):
    t = threading.Timer(seconds, _fire_reminder, args=(text,))
    t.daemon = True
    t.start()


DURATION_RE = re.compile(
    r"(\d+)\s*(second|seconds|minute|minutes|hour|hours)"
)


def parse_duration_to_seconds(text: str):
    match = DURATION_RE.search(text)
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    if "second" in unit:
        return value
    if "minute" in unit:
        return value * 60
    if "hour" in unit:
        return value * 3600
    return None


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_name():
    say_variant(
        "I'm Dora, your voice assistant.",
        "My name is Dora — happy to help.",
        "Dora here!",
    )


def cmd_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    say_variant(f"It's {now} right now.", f"The time is {now}.")


def cmd_date():
    today = datetime.datetime.now().strftime("%A, %B %d, %Y")
    speak(f"Today is {today}.")


def cmd_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        say_variant("Good morning!", "Morning! Ready when you are.")
    elif hour < 18:
        say_variant("Good afternoon!", "Hey, good afternoon.")
    else:
        say_variant("Good evening!", "Evening! What do you need?")


def cmd_youtube():
    speak("Opening YouTube.")
    webbrowser.open("https://www.youtube.com/")


def cmd_vgi():
    speak("Opening VGI.")
    webbrowser.open("https://vgiagencies.vercel.app/")


def cmd_google_search(query: str):
    query = re.sub(r"\b(search|for|google)\b", "", query).strip()
    if not query:
        speak("What should I search for?")
        query = listen()
        if not query:
            speak("Never mind, cancelling that.")
            return
    speak(f"Here's what I found for {query}.")
    webbrowser.open(f"https://www.google.com/search?q={query}")


def cmd_wikipedia(query: str):
    if not HAS_WIKI:
        speak("I need the wikipedia package installed for that.")
        return
    topic = re.sub(r"\b(wikipedia|who is|what is|tell me about)\b", "", query).strip()
    if not topic:
        speak("Who or what should I look up?")
        topic = listen()
    try:
        summary = wikipedia.summary(topic, sentences=2)
        speak(summary)
    except wikipedia.exceptions.DisambiguationError:
        speak("That could mean a few different things — can you be more specific?")
    except Exception:
        speak("I couldn't find anything on that.")


def cmd_weather(query: str):
    if not HAS_REQUESTS or not WEATHER_API_KEY:
        speak("Weather isn't set up yet — add an API key in the config to enable it.")
        return
    city = re.sub(r"\b(weather|in|the|today)\b", "", query).strip() or "Kolkata"
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url, timeout=5).json()
        if data.get("cod") != 200:
            speak(f"I couldn't find weather for {city}.")
            return
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        speak(f"It's {temp} degrees Celsius and {desc} in {city}.")
    except Exception:
        speak("I couldn't reach the weather service.")


def cmd_joke():
    joke = pyjokes.get_joke(language="en", category=random.choice(["neutral", "chuck", "all"]))
    speak(joke)


def cmd_calculate(text: str):
    expr = re.sub(r"\b(calculate|what is|what's|equals|equal to)\b", "", text)
    expr = expr.replace("plus", "+").replace("minus", "-")
    expr = expr.replace("times", "*").replace("multiplied by", "*")
    expr = expr.replace("divided by", "/").replace("x", "*")
    expr = re.sub(r"[^0-9+\-*/.() ]", "", expr).strip()
    if not expr:
        speak("I didn't catch a valid expression.")
        return
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        speak(f"That's {result}.")
    except Exception:
        speak("Sorry, I couldn't work that out.")


def cmd_timer(text: str):
    seconds = parse_duration_to_seconds(text)
    if not seconds:
        speak("How long should the timer be? For example, 'set a timer for 5 minutes'.")
        return
    label_match = re.search(r"for (?:my |the )?(.+?)(?: timer)?$", text)
    set_timer(seconds, "")
    say_variant(f"Timer set for {seconds // 60} minutes and {seconds % 60} seconds." if seconds >= 60
                else f"Timer set for {seconds} seconds.")


def cmd_reminder(text: str):
    seconds = parse_duration_to_seconds(text)
    reminder_text = re.sub(r"remind me to|in \d+.*", "", text).strip()
    if not seconds:
        speak("When should I remind you? Try 'remind me to call mom in 10 minutes'.")
        return
    set_reminder(seconds, reminder_text or "your reminder")
    speak(f"Got it, I'll remind you in {seconds // 60 or seconds} "
          f"{'minutes' if seconds >= 60 else 'seconds'}.")


def cmd_coin_flip():
    speak(random.choice(["Heads!", "Tails!"]))


def cmd_dice_roll():
    speak(f"You rolled a {random.randint(1, 6)}.")


def cmd_spell(text: str):
    word = re.sub(r"\b(spell)\b", "", text).strip()
    if not word:
        speak("What word should I spell?")
        word = listen()
    speak(", ".join(word.upper()))


def cmd_help():
    speak(
        "You can ask me for the time or date, tell you a joke, do a calculation, "
        "set a timer or reminder, search Google or Wikipedia, check the weather, "
        "flip a coin, roll a dice, or spell a word."
    )


# ---------------------------------------------------------------------------
# Command routing
# ---------------------------------------------------------------------------

def handle_command(text: str) -> bool:
    if any(w in text for w in EXIT_WORDS):
        speak("Alright, talk soon!")
        return False

    if "your name" in text:
        cmd_name()
    elif "time" in text and "timer" not in text:
        cmd_time()
    elif "date" in text or "day is it" in text:
        cmd_date()
    elif "hello" in text or "hi dora" in text:
        cmd_greeting()
    elif "youtube" in text:
        cmd_youtube()
    elif "vgi" in text:
        cmd_vgi()
    elif "wikipedia" in text or text.startswith(("who is", "what is", "tell me about")):
        cmd_wikipedia(text)
    elif "search" in text or "google" in text:
        cmd_google_search(text)
    elif "weather" in text:
        cmd_weather(text)
    elif "joke" in text:
        cmd_joke()
    elif "calculate" in text or "what is" in text or "what's" in text:
        cmd_calculate(text)
    elif "timer" in text:
        cmd_timer(text)
    elif "remind me" in text:
        cmd_reminder(text)
    elif "flip a coin" in text or "coin flip" in text:
        cmd_coin_flip()
    elif "roll a dice" in text or "roll a die" in text:
        cmd_dice_roll()
    elif "spell" in text:
        cmd_spell(text)
    elif "help" in text or "what can you do" in text:
        cmd_help()
    else:
        say_variant(
            "I'm not sure how to help with that yet.",
            "Sorry, I don't know that one.",
            "I didn't quite get that — try asking differently.",
        )

    return True


# ---------------------------------------------------------------------------
# Main loop: wake word -> answer -> short follow-up window (no wake word needed)
# ---------------------------------------------------------------------------

def follow_up_loop():
    """After answering, listen briefly for a follow-up question without
    requiring the wake word again — mimics Google Assistant's continued
    conversation mode."""
    end_time = time.time() + FOLLOW_UP_SECONDS
    while time.time() < end_time:
        remaining = end_time - time.time()
        heard = listen(timeout=min(remaining, FOLLOW_UP_SECONDS), phrase_time_limit=8)
        if heard:
            if not handle_command(heard):
                return False
            end_time = time.time() + FOLLOW_UP_SECONDS  # extend window after each reply
    return True


def main():
    speak("Dora is ready. Say 'hey Dora' any time.")
    running = True

    while running:
        heard = listen()
        if not heard:
            continue

        if any(w in heard for w in WAKE_WORDS):
            say_variant("Yes?", "I'm listening.", "Go ahead.")
            command = listen()
            if command:
                running = handle_command(command)
                if running:
                    running = follow_up_loop()
        elif any(w in heard for w in EXIT_WORDS):
            running = handle_command(heard)


if __name__ == "__main__":
    main()