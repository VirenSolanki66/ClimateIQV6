import requests
import streamlit as st

def get_gemini_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None

def ask_ai(question, weather_context=None):
    api_key = get_gemini_key()
    
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        return "⚠️ Gemini API key not set. Add GEMINI_API_KEY in Streamlit Secrets."

    # Updated model name — gemini-pro is deprecated
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-1.5-flash:generateContent?key={api_key}"
    )

    system_prompt = (
        "You are ClimateIQ, an AI assistant for weather, climate, "
        "air quality, health, and travel safety. Give helpful answers."
    )

    if weather_context:
        system_prompt += (
            f" Current weather — City: {weather_context.get('city')}, "
            f"Temp: {weather_context.get('temp')}°C, "
            f"Humidity: {weather_context.get('humidity')}%, "
            f"Wind: {weather_context.get('wind')} m/s."
        )

    full_prompt = f"{system_prompt}\n\nUser: {question}"

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"maxOutputTokens": 500}
    }

    try:
        res = requests.post(url, json=payload, timeout=15)
        data = res.json()

        # Safe extraction with clear error messages
        if "candidates" not in data:
            error_msg = data.get("error", {}).get("message", str(data))
            return f"❌ Gemini Error: {error_msg}"

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"❌ Network Error: {str(e)}"
