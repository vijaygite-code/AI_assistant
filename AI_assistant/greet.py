import os
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# WeatherAPI key (loaded from .env file)
API_KEY = os.getenv("WEATHER_API_KEY")

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)  # Timeout to prevent hanging
        except sr.WaitTimeoutError:
            print("Listening timed out, no speech detected.")
            return ""
        
    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-US')
        print(f"User said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Can you please repeat?")
        return ""
    except sr.RequestError:
        print("Sorry, my speech service is down")
        return ""

def get_weather(city):
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": API_KEY,
        "q": city,
        "aqi": "no"  # Optional: set to "yes" if you want air quality information
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Will raise an exception for 4xx/5xx status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return "Sorry, I couldn't fetch the weather information at the moment."
    
    if response.status_code == 200:
        data = response.json()
        temperature = data['current']['temp_c']
        description = data['current']['condition']['text']
        return f"The current temperature in {city} is {temperature}°C with {description}."
    else:
        return "Sorry, I couldn't fetch the weather information at the moment."

def process_command(command):
    if "weather" in command:
        speak("Sure, for which city would you like the weather update?")
        city = listen()
        if city:  # Check if a city was actually provided
            weather_info = get_weather(city)
            speak(weather_info)

    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The current time is {current_time}")

    elif "date" in command:
        current_date = datetime.date.today().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")

    elif "exit" in command or "bye" in command:
        speak("Goodbye! Have a great day!")
        return False
    else:
        speak("I'm not sure how to help with that. Can you please try again?")
    return True

speak("Hello! I'm your AI assistant. How can I help you today?")

while True:
    command = listen()
    if not process_command(command):
        break
