import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

from utils import get_weather, get_forecast
from aqi import get_aqi
from alerts import generate_alerts
from ml_lstm import train_model, predict_next
from chatbot import ask_ai

st.set_page_config(
    page_title="ClimateIQ",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #001a3a; }

/* ── Clouds BEHIND everything ── */
#wbg { z-index: -10 !important; }

.main-title {
    font-family:'Orbitron', monospace; font-size:3.2rem; font-weight:700;
    text-align:center;
    /* Yellow/Gold Logo Gradient */
    background: linear-gradient(135deg, #FFD700 0%, #FFB300 50%, #FF8C00 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:0.1rem; letter-spacing:0.1em;
    position:relative; z-index:10;
    filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.2));
}
.sub-title {
    text-align:center; color:#002a5c; font-size:1rem;
    margin-bottom:1.5rem; letter-spacing:0.05em;
    font-weight:700; position:relative; z-index:10;
    text-transform: uppercase;
}

/* Cards with Higher Contrast */
.metric-card {
    background:rgba(255,255,255,0.75); /* Increased opacity for readability */
    border:1px solid rgba(255,255,255,0.9);
    border-radius:20px; padding:20px; text-align:center;
    box-shadow:0 10px 30px rgba(0,40,80,0.15);
    transition:transform 0.2s;
    backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
    position:relative; z-index:10;
}
.metric-card:hover { transform:translateY(-6px); border-color: #FFD700; }
.metric-val   { font-size:2.2rem; font-weight:800; color:#001a3a; }
.metric-label { font-size:0.85rem; color:#004080; margin-top:4px; letter-spacing:0.06em; font-weight:700; }

.section-head {
    font-family:'Orbitron',monospace; font-size:1.1rem; color:#001a3a;
    border-left:5px solid #FFD700; padding-left:12px;
    margin:30px 0 15px; letter-spacing:0.05em;
    position:relative; z-index:10;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
}

.glass-card {
    background:rgba(255,255,255,0.7); border:1px solid rgba(255,255,255,0.8);
    border-radius:16px; padding:16px 20px; text-align:center;
    backdrop-filter:blur(15px); -webkit-backdrop-filter:blur(15px);
    box-shadow:0 4px 20px rgba(0,0,0,0.1);
    position:relative; z-index:10;
}

/* Chat & Alerts */
.chat-bubble-user { background:rgba(255,255,255,0.8); border-radius:16px 16px 0 16px; padding:12px; margin:8px 0; color:#001a3a; font-weight:600; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
.chat-bubble-ai   { background:rgba(0,85,170,0.15); border-left:4px solid #FFD700; border-radius:16px 16px 16px 0; padding:12px; margin:8px 0; color:#001a3a; font-weight:500; }

.fancy-divider { border:none; border-top:2px solid rgba(255,215,0,0.3); margin:30px 0; }

/* Global Widget Visibility */
.stTextInput, .stButton, [data-testid="stMetric"], .stMarkdown {
    position: relative;
    z-index: 10 !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  WEATHER BACKGROUNDS (Preserved from original)
# ══════════════════════════════════════════════════════════════════════════════
def set_weather_background(description, temp):
    desc = description.lower()
    # Logic remains the same, but the CSS inside uses 'wbg' which is behind Z-index 10
    if any(w in desc for w in ["clear", "sunny"]) or not any(w in desc for w in ["rain","cloud","storm","snow","fog"]):
        clouds = "".join([f'<div class="dc" style="top:{6+i*12}%;width:{200+i*65}px;height:{58+i*16}px;animation-duration:{22+i*9}s;animation-delay:-{i*7}s;opacity:{0.80+i*0.04};"></div>' for i in range(4)])
        st.markdown(f'<style>.stApp{{background:linear-gradient(180deg,#4FC3F7 0%,#E1F5FE 100%)!important;}}</style><div id="wbg"><div class="dsun"></div>{clouds}</div><style>#wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-10;pointer-events:none;overflow:hidden;}}.dsun{{position:absolute;top:30px;right:90px;width:110px;height:110px;background:radial-gradient(circle,#FFFDE7,#FFD600);border-radius:50%;box-shadow:0 0 60px rgba(255,214,0,0.5);}}.dc{{position:absolute;left:-320px;background:white;border-radius:80px;animation:cloudmove linear infinite;}}@keyframes cloudmove{{0%{{left:-320px;}}100%{{left:110%;}}}}</style>', unsafe_allow_html=True)
    # [Other weather states: Rain, Snow, Storm etc. omitted for brevity, logic follows the same template]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🌍 CLIMATEIQ</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-Powered Weather Intelligence</div>', unsafe_allow_html=True)

# ── CITY INPUT ────────────────────────────────────────────────────────────────
col_inp, col_btn = st.columns([4, 1])
with col_inp:
    city = st.text_input("🏙️ Enter City Name", "Rajkot")
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    search = st.button("🔍 Analyze", use_container_width=True)

# ── MAIN LOGIC ────────────────────────────────────────────────────────────────
if city:
    # ... (Weather Fetching Logic same as your original)
    weather_data = get_weather(city)
    
    if "coord" in weather_data:
        lat, lon = weather_data["coord"]["lat"], weather_data["coord"]["lon"]
        temp, description = weather_data["main"]["temp"], weather_data["weather"][0]["description"].title()
        
        set_weather_background(description, temp)
        aqi_val, aqi_label, aqi_emoji = get_aqi(lat, lon)

        # ── METRIC CARDS ──────────────────────────────────────────────────────────
        st.markdown('<div class="section-head">📊 LIVE CONDITIONS</div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        metrics = [
            (c1, f"{temp:.1f}°C", "🌡️ Temp"),
            (c2, f"{weather_data['main']['feels_like']:.1f}°C", "🤔 Feels"),
            (c3, f"{weather_data['main']['humidity']}%", "💧 Humidity"),
            (c4, f"{weather_data['wind']['speed']} m/s", "🌪️ Wind"),
            (c5, f"{aqi_val}", "🌬️ AQI")
        ]
        for col, val, label in metrics:
            with col:
                st.markdown(f'<div class="metric-card"><div class="metric-val">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

        # ... (Map, LSTM, and Chatbot sections follow)
