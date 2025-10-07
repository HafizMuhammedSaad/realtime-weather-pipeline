import requests
import sqlite3
import os
import json
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()  # loads API_KEY from .env or GitHub Actions secrets

# --- Configuration ---
API_KEY = os.getenv("API_KEY")
CITIES = ["Karachi", "Lahore", "Islamabad", "London", "New York"]
DB_PATH = "weather_data.db"

def fetch_weather(city):
    """Fetch weather data from OpenWeatherMap API."""
    if not API_KEY:
        raise ValueError("❌ API_KEY is missing. Please set it in .env or GitHub Secrets.")
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data


def insert_weather(city, temp, humidity, desc, pressure):
    """Insert weather data into local SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temperature REAL,
            humidity REAL,
            description TEXT,
            pressure REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert record
    cursor.execute(
        "INSERT INTO weather_data (city, temperature, humidity, description, pressure) VALUES (?, ?, ?, ?, ?)",
        (city, temp, humidity, desc, pressure)
    )

    conn.commit()
    conn.close()


# --- Main ETL Loop ---
for city in CITIES:
    data = fetch_weather(city)

    # ✅ Safety check to avoid KeyError
    if "main" in data and "weather" in data:
        temp = data["main"].get("temp")
        humidity = data["main"].get("humidity")
        pressure = data["main"].get("pressure")
        desc = data["weather"][0].get("description", "N/A")

        insert_weather(city, temp, humidity, desc, pressure)
        print(f"✅ {city} inserted: {temp}°C, {humidity}% humidity, {pressure} hPa, {desc}")
    else:
        print(f"⚠️ Skipped {city} — Invalid response: {json.dumps(data, indent=2)}")
