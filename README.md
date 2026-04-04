# 🌍 ClimateIQ — AI Powered Weather Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **Microsoft Elevate Internship — Capstone Project 2026**
> Built by **Solanki Viren Maheshbhai** | GEC Bhavnagar | ECE Sem 8

---

## 🚀 Live Demo

[[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-link.streamlit.app)
](https://climateiqv6.streamlit.app/)
> Replace the link above with your actual Streamlit Cloud URL after deployment.

---

## 📌 About The Project

**ClimateIQ** is a real-time AI-powered weather intelligence platform that addresses the challenge of unpredictable climate patterns impacting agriculture, health, and daily life in India.

The platform combines **live weather data**, **LSTM machine learning predictions**, **AQI monitoring**, and a **Gemini AI chatbot** into a single beautifully designed web application.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🌡️ **Live Weather** | Real-time temperature, humidity, wind, pressure, visibility |
| 🌫️ **AQI Monitor** | Air Quality Index (1–5) with health advice |
| ⚠️ **Smart Alerts** | Auto warnings for heatwave, storm, poor air, cold |
| 🧠 **LSTM Prediction** | AI-predicted 7-day temperature forecast |
| 📈 **5-Day Forecast** | Interactive Plotly chart from OpenWeatherMap |
| 📍 **Live Map** | Folium map with city location marker |
| 🤖 **AI Chatbot** | Gemini AI for weather, health & travel queries |
| 🎨 **Dynamic UI** | Animated weather backgrounds (rain, snow, sun, storm, fog) |
| 🕐 **Live Clock** | Real-time clock with Morning/Afternoon/Evening/Night badge |
| 📱 **Responsive** | Works on desktop, tablet, and mobile |

---

## 🛠️ Tech Stack

```
Frontend       →  Streamlit + Custom CSS + JavaScript
ML Model       →  TensorFlow LSTM Neural Network
Charts         →  Plotly Graph Objects
Map            →  Folium + Streamlit-Folium
Weather API    →  OpenWeatherMap (Current + Forecast + AQI)
AI Chatbot     →  Google Gemini 2.0 Flash API
Deployment     →  Streamlit Cloud
Version Control→  GitHub
```

---

## 📁 Project Structure

```
ClimateIQ/
│
├── app.py              ← Main Streamlit app (UI + logic)
├── utils.py            ← OpenWeatherMap API calls
├── aqi.py              ← Air Quality Index fetch
├── alerts.py           ← Smart weather alert logic
├── ml_lstm.py          ← LSTM model training + prediction
├── chatbot.py          ← Gemini AI chatbot integration
├── requirements.txt    ← Python dependencies
├── .gitignore          ← Ignore secrets & cache
│
└── .streamlit/
    ├── config.toml     ← Theme & server config
    └── secrets.toml    ← API keys (NOT on GitHub)
```

---

## ⚙️ Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ClimateIQ.git
cd ClimateIQ
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add API Keys
Create `.streamlit/secrets.toml` file:
```toml
OPENWEATHER_API_KEY = "your_openweathermap_key"
GEMINI_API_KEY = "your_gemini_api_key"
```

### 4. Run the App
```bash
streamlit run app.py
```

---

## 🔑 API Keys Setup

| API | Get Free Key |
|---|---|
| OpenWeatherMap | [openweathermap.org/api](https://openweathermap.org/api) |
| Google Gemini | [aistudio.google.com](https://aistudio.google.com/app/apikey) |

---

## ☁️ Deploy on Streamlit Cloud

1. Push code to GitHub (without `secrets.toml`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repo → Select `app.py`
4. Add secrets in **Settings → Secrets**:
```toml
OPENWEATHER_API_KEY = "your_key"
GEMINI_API_KEY = "your_key"
```
5. Click **Deploy** 🚀

---

## 🧠 LSTM Model Architecture

```
Input: 3 time steps of temperature data
         ↓
LSTM Layer (64 units, ReLU activation)
         ↓
Dense Layer (32 units, ReLU activation)
         ↓
Output: Next temperature prediction
         ↓
Repeated 7 times → 7-day forecast
```

**Training:** 100 epochs | Adam optimizer | MSE loss | ~10 seconds

---

## 🌦️ Weather Background Effects

| Condition | Background Effect |
|---|---|
| ☀️ Clear / Sunny | Sky blue + glowing sun + spinning rays + floating clouds |
| 🌧️ Rain / Drizzle | Dark blue + animated raindrops + lightning flash |
| ⛈️ Thunderstorm | Black sky + heavy rain + bright lightning bursts |
| ❄️ Snow / Temp < 2°C | Deep navy + rotating snowflakes |
| 🌫️ Fog / Mist / Haze | Grey gradient + drifting fog layers |
| ☁️ Cloudy | Blue sky + multi-speed parallax clouds |

---

## 📸 Screenshots

> Add your app screenshots here after deployment.

---

## 📋 Requirements

```txt
streamlit
plotly
folium
streamlit-folium
requests
pandas
numpy
scikit-learn
tensorflow-cpu
```

---

## 👨‍💻 Author

**Solanki Viren Maheshbhai**
- 🎓 B.E. Electronics & Communication Engineering — GEC Bhavnagar
- 🏢 Microsoft Elevate Internship — FICE Education Pvt. Ltd.
- 📧 solvir66@gmail.com
- 🆔 Enrollment: 220210111035

---

## 🏆 Project Info

| Field | Details |
|---|---|
| Project Title | ClimateIQ — AI Powered Weather Intelligence Platform |
| Domain | AI & Machine Learning |
| Organization | FICE Education Pvt. Ltd. (Microsoft Elevate) |
| College | Government Engineering College, Bhavnagar |
| Internal Guide | Mr. Sarvaiya Ashish Kalubhai |
| External Guide | Adarsh — FICE Education |
| Year | 2026 |

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

- [OpenWeatherMap](https://openweathermap.org) — Weather data API
- [Google Gemini](https://deepmind.google/technologies/gemini) — AI chatbot
- [Streamlit](https://streamlit.io) — Web framework
- [TensorFlow](https://tensorflow.org) — ML framework
- Microsoft Elevate & FICE Education for internship opportunity

---

<div align="center">
  Made with ❤️ by Viren Solanki | GTU 2026
</div>
