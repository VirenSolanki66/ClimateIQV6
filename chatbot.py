import requests
import streamlit as st

def get_gemini_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None

def ask_ai(question, weather_context=None):
    """
    Ask Gemini AI a weather/climate related question.
    weather_context: optional dict with city weather data to inject.
    Returns answer string.
    """
    api_key = get_gemini_key()
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        return (
            "⚠️ Gemini API key not configured.\n\n"
            "Add your key to `.streamlit/secrets.toml`:\n"
            "```\nGEMINI_API_KEY = 'your-key-here'\n```\n"
            "Get a free key at: https://makersuite.google.com/app/apikey"
        )

    # Build prompt with optional weather context
    system_prompt = (
        "You are ClimateIQ, an expert AI assistant for weather, climate change, "
        "air quality, health advice, and travel safety. "
        "Give concise, helpful, and accurate answers. "
        "If asked about climate change, relate it to real-world impact."
    )

    if weather_context:
        ctx = (
            f"\nCurrent weather context — City: {weather_context.get('city', 'Unknown')}, "
            f"Temp: {weather_context.get('temp', 'N/A')}°C, "
            f"Humidity: {weather_context.get('humidity', 'N/A')}%, "
            f"Wind: {weather_context.get('wind', 'N/A')} m/s."
        )
        system_prompt += ctx

    full_prompt = f"{system_prompt}\n\nUser question: {question}"

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-pro:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}]
    }

    try:
        res = requests.post(url, json=payload, timeout=15)
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"❌ Error from Gemini API: {str(e)}"
