import requests
import streamlit as st

# ✅ API KEY — Replace with your OpenWeatherMap key
# For Streamlit Cloud: Store in .streamlit/secrets.toml
def get_api_key():
    try:
        return st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        return "YOUR_OPENWEATHER_API_KEY"  # fallback for local testing

def get_weather(city):
    """Fetch current weather data for a city."""
    API_KEY = get_api_key()
    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_forecast(city):
    """Fetch 5-day / 3-hour forecast data for a city."""
    API_KEY = get_api_key()
    url = (
        f"http://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
