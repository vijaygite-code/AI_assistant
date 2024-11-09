import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API key from the .env file
API_KEY = os.getenv("API_KEY")

def get_weather(city):
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": API_KEY,
        "q": city,
        "aqi": "no"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        temperature = data['current']['temp_c']
        description = data['current']['condition']['text']
        return f"The current temperature in {city} is {temperature}°C with {description}."
    else:
        return "Sorry, I couldn't fetch the weather information at the moment."
    
########################################################################################################################################

def check_weather_api(api_key, city):
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city,
        "aqi": "no"  # You can set this to "yes" if you want air quality information
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        
        data = response.json()
        temperature = data['current']['temp_c']
        description = data['current']['condition']['text']
        
        print("API is working correctly!")
        print(f"Current weather in {city}:")
        print(f"Temperature: {temperature}°C")
        print(f"Description: {description}")
    
    except requests.exceptions.HTTPError as http_err:
        error_message = response.json().get("error", {}).get("message", "Unknown error")
        print(f"HTTP error occurred: {http_err}")
        print(f"Error message from API: {error_message}")
    except Exception as err:
        print(f"An error occurred: {err}")

# You can change this to any city you want to test
CITY = "Pune"

# Check if API key is loaded
if API_KEY:
    check_weather_api(API_KEY, CITY)
else:
    print("API key not found. Please make sure it's set in the .env file.")
