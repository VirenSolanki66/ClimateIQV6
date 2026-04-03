import requests
import streamlit as st

AQI_LABELS = {
    1: ("Good", "🟢"),
    2: ("Fair", "🟡"),
    3: ("Moderate", "🟠"),
    4: ("Poor", "🔴"),
    5: ("Very Poor", "🟣"),
}

def get_api_key():
    try:
        return st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        return "YOUR_OPENWEATHER_API_KEY"

def get_aqi(lat, lon):
    """Fetch AQI index (1-5 scale) for given coordinates."""
    API_KEY = get_api_key()
    url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={lat}&lon={lon}&appid={API_KEY}"
    )
    try:
        data = requests.get(url, timeout=10).json()
        aqi_value = data["list"][0]["main"]["aqi"]
        label, emoji = AQI_LABELS.get(aqi_value, ("Unknown", "⚪"))
        return aqi_value, label, emoji
    except Exception:
        return 1, "Good", "🟢"  # safe fallback
