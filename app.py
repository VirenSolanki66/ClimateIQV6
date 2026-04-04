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
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #002a5c; }
#wbg { z-index: -10 !important; }
.main-title {
    font-family:'Orbitron',monospace; font-size:2.8rem; font-weight:700;
    text-align:center;
    background:linear-gradient(135deg,#0055aa,#007FFF,#00C9A7);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:0.2rem; letter-spacing:0.08em;
    position:relative; z-index:10;
}
.sub-title {
    text-align:center; color:#003d7a; font-size:0.95rem;
    margin-bottom:0.5rem; letter-spacing:0.04em;
    font-weight:600; position:relative; z-index:10;
}
.clock-bar { text-align:center; padding:8px 0 16px; position:relative; z-index:10; }
.clock-time {
    font-family:'Orbitron',monospace; font-size:2rem;
    color:#003d7a; font-weight:700; letter-spacing:0.1em;
    text-shadow: 0 2px 8px rgba(255,255,255,0.6);
}
.clock-date { font-size:0.9rem; color:#004a8f; font-weight:600; margin-top:2px; letter-spacing:0.05em; }
.day-badge {
    display:inline-block; margin-left:10px;
    padding:3px 14px; border-radius:999px;
    font-size:0.82rem; font-weight:700;
    letter-spacing:0.04em; vertical-align:middle;
}
.metric-card {
    background:rgba(255,255,255,0.55);
    border:1px solid rgba(255,255,255,0.7);
    border-radius:20px; padding:20px; text-align:center;
    box-shadow:0 8px 32px rgba(0,80,160,0.10);
    transition:transform 0.2s;
    backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
    position:relative; z-index:10;
}
.metric-card:hover { transform:translateY(-4px); }
.metric-val   { font-size:2rem; font-weight:700; color:#003d7a; }
.metric-label { font-size:0.8rem; color:#0055aa; margin-top:4px; letter-spacing:0.05em; font-weight:600; }
.section-head {
    font-family:'Orbitron',monospace; font-size:1.05rem; color:#003d7a;
    border-left:4px solid #0077cc; padding-left:10px;
    margin:24px 0 12px; letter-spacing:0.04em;
    position:relative; z-index:10;
}
.glass-card {
    background:rgba(255,255,255,0.55); border:1px solid rgba(255,255,255,0.7);
    border-radius:16px; padding:14px 18px; text-align:center;
    backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
    box-shadow:0 4px 20px rgba(0,80,160,0.08);
    position:relative; z-index:10;
}
.alert-error   { background:rgba(255,80,80,0.18); border-left:4px solid #FF5252; padding:10px 16px; border-radius:10px; margin:6px 0; backdrop-filter:blur(8px); position:relative; z-index:10; }
.alert-warning { background:rgba(255,193,7,0.18); border-left:4px solid #FFC107; padding:10px 16px; border-radius:10px; margin:6px 0; backdrop-filter:blur(8px); position:relative; z-index:10; }
.alert-info    { background:rgba(41,182,246,0.18); border-left:4px solid #29B6F6; padding:10px 16px; border-radius:10px; margin:6px 0; backdrop-filter:blur(8px); position:relative; z-index:10; }
.aqi-pill { display:inline-block; padding:6px 18px; border-radius:999px; font-weight:700; font-size:1rem; margin-top:4px; }
.chat-bubble-user { background:rgba(255,255,255,0.55); border:1px solid rgba(255,255,255,0.6); padding:10px 16px; border-radius:16px 16px 0 16px; margin:6px 0; color:#002a5c; font-weight:500; position:relative; z-index:10; }
.chat-bubble-ai   { background:rgba(0,100,200,0.12); border:1px solid rgba(0,150,255,0.25); padding:10px 16px; border-radius:16px 16px 16px 0; margin:6px 0; border-left:3px solid #0077cc; color:#001a3a; position:relative; z-index:10; }
.fancy-divider { border:none; border-top:1px solid rgba(0,100,200,0.2); margin:24px 0; position:relative; z-index:10; }
.stTextInput, .stButton, .stSpinner, .stAlert,
[data-testid="stMetric"], [data-testid="column"],
.element-container, .stMarkdown {
    position: relative;
    z-index: 10 !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  WEATHER BACKGROUND
# ══════════════════════════════════════════════════════════════════════════════
def set_weather_background(description, temp):
    desc = description.lower()

    # ☀️ CLEAR / SUNNY
    if any(w in desc for w in ["clear", "sunny"]) or not any(
        w in desc for w in ["rain","drizzle","shower","thunder","storm","snow","blizzard","sleet","fog","mist","haze","smoke","dust","cloud"]
    ):
        # 3 layers: fast small, medium, slow large — realistic parallax
        clouds = ""
        cloud_data = [
            (4,  150, 45,  7,  0,   0.75),
            (14, 240, 65,  10, -3,  0.85),
            (24, 190, 55,  8,  -1,  0.70),
            (34, 310, 80,  13, -5,  0.90),
            (44, 170, 50,  9,  -2,  0.78),
            (54, 260, 70,  11, -4,  0.82),
        ]
        for top, w, h, dur, delay, op in cloud_data:
            clouds += f'<div class="dc" style="top:{top}%;width:{w}px;height:{h}px;animation-duration:{dur}s;animation-delay:{delay}s;opacity:{op};"></div>'

        st.markdown(f"""
        <style>.stApp{{background:linear-gradient(180deg,#4FC3F7 0%,#81D4FA 28%,#B3E5FC 58%,#E1F5FE 82%,#f0faff 100%)!important;}}</style>
        <div id="wbg">
            <div class="dsun"></div>
            <div class="dray dr1"></div><div class="dray dr2"></div>
            <div class="dray dr3"></div><div class="dray dr4"></div>
            <div class="dray dr5"></div><div class="dray dr6"></div>
            {clouds}
        </div>
        <style>
        #wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-10;pointer-events:none;overflow:hidden;}}
        .dsun{{position:absolute;top:30px;right:90px;width:110px;height:110px;
            background:radial-gradient(circle,#FFFDE7 10%,#FFE57F 40%,#FFD600 70%,#FFB300 100%);
            border-radius:50%;
            box-shadow:0 0 0 18px rgba(255,230,80,0.14),0 0 0 36px rgba(255,200,0,0.09),0 0 70px 25px rgba(255,210,0,0.35);
            animation:sunpulse 4s ease-in-out infinite;}}
        @keyframes sunpulse{{
            0%,100%{{box-shadow:0 0 0 18px rgba(255,230,80,0.14),0 0 0 36px rgba(255,200,0,0.09),0 0 70px 25px rgba(255,210,0,0.35);}}
            50%{{box-shadow:0 0 0 24px rgba(255,230,80,0.22),0 0 0 48px rgba(255,200,0,0.12),0 0 100px 40px rgba(255,210,0,0.52);}}
        }}
        .dray{{position:absolute;top:83px;right:145px;width:75px;height:4px;
            background:linear-gradient(90deg,rgba(255,230,50,0.85),transparent);
            border-radius:4px;transform-origin:right center;animation:rayspin 12s linear infinite;}}
        .dr1{{transform:rotate(0deg);}}.dr2{{transform:rotate(60deg);}}.dr3{{transform:rotate(120deg);}}
        .dr4{{transform:rotate(180deg);}}.dr5{{transform:rotate(240deg);}}.dr6{{transform:rotate(300deg);}}
        @keyframes rayspin{{from{{transform:rotate(0deg);}}to{{transform:rotate(360deg);}}}}
        .dc{{position:absolute;left:-350px;
            background:rgba(255,255,255,0.92);
            border-radius:80px;
            box-shadow:0 6px 20px rgba(100,160,220,0.10),inset 0 -4px 10px rgba(180,220,255,0.15);
            animation:cloudmove linear infinite;}}
        .dc::before{{content:'';position:absolute;top:-50%;left:15%;width:52%;height:140%;background:rgba(255,255,255,0.95);border-radius:50%;}}
        .dc::after{{content:'';position:absolute;top:-38%;left:48%;width:40%;height:115%;background:rgba(245,252,255,0.90);border-radius:50%;}}
        @keyframes cloudmove{{0%{{left:-350px;}}100%{{left:110%;}}}}
        </style>""", unsafe_allow_html=True)

    # ⛈️ THUNDERSTORM
    elif any(w in desc for w in ["thunder", "storm", "tornado"]):
        drops = "".join([
            f'<div class="hd" style="left:{i*2}%;animation-delay:{round((i*0.08)%1.5,2)}s;animation-duration:{round(0.3+(i%4)*0.1,2)}s;height:{15+(i%6)*4}px;"></div>'
            for i in range(50)
        ])
        st.markdown(f"""
        <style>.stApp{{background:linear-gradient(180deg,#050505 0%,#1a0800 40%,#2d1000 100%)!important;}}</style>
        <div id="wbg">{drops}<div class="bflash"></div></div>
        <style>
        #wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-10;pointer-events:none;overflow:hidden;}}
        .hd{{position:absolute;top:-20px;width:2px;background:linear-gradient(180deg,transparent,#78909C);border-radius:2px;animation:hfall linear infinite;}}
        @keyframes hfall{{0%{{top:-20px;}}100%{{top:110%;}}}}
        .bflash{{position:absolute;top:0;left:0;width:100%;height:100%;animation:blight 4s ease-in-out infinite;}}
        @keyframes blight{{0%,78%,83%,86%,100%{{background:rgba(255,255,255,0);}}79%,82%{{background:rgba(255,220,100,0.1);}}80%{{background:rgba(255,255,255,0.2);}}}}
        </style>""", unsafe_allow_html=True)

    # 🌧️ RAIN
    elif any(w in desc for w in ["rain", "drizzle", "shower"]):
        drops = "".join([
            f'<div class="rd" style="left:{i*2.5}%;animation-delay:{round((i*0.13)%2.0,2)}s;animation-duration:{round(0.5+(i%6)*0.12,2)}s;height:{8+(i%8)*3}px;opacity:{round(0.3+(i%5)*0.12,2)};"></div>'
            for i in range(40)
        ])
        st.markdown(f"""
        <style>.stApp{{background:linear-gradient(180deg,#0d1b2a 0%,#1a2f4a 50%,#0f2a3d 100%)!important;}}</style>
        <div id="wbg">{drops}<div class="loverlay"></div></div>
        <style>
        #wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-10;pointer-events:none;overflow:hidden;}}
        .rd{{position:absolute;top:-20px;width:2px;background:linear-gradient(180deg,transparent,#81D4FA);border-radius:2px;animation:rfall linear infinite;}}
        @keyframes rfall{{0%{{top:-20px;}}100%{{top:110%;}}}}
        .loverlay{{position:absolute;top:0;left:0;width:100%;height:100%;animation:lflash 7s ease-in-out infinite;}}
        @keyframes lflash{{0%,88%,92%,100%{{background:rgba(255,255,255,0);}}90%{{background:rgba(200,230,255,0.10);}}}}
        </style>""", unsafe_allow_html=True)

    # ❄️ SNOW
    elif any(w in desc for w in ["snow","blizzard","sleet"]) or temp < 2:
        flakes = "".join([
            f'<div class="sf" style="left:{i*2.7}%;animation-delay:{round((i*0.18)%5,2)}s;animation-duration:{round(3+(i%5),2)}s;font-size:{8+(i%4)*5}px;opacity:{round(0.4+(i%4)*0.15,2)};color:#B3E5FC;">❄</div>'
            for i in range(37)
        ])
        st.markdown(f"""
        <style>.stApp{{background:linear-gradient(180deg,#050a1a 0%,#0a1628 50%,#1a2a40 100%)!important;}}</style>
        <div id="wbg">{flakes}</div>
        <style>
        #wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-10;pointer-events:none;overflow:hidden;}}
        .sf{{position:absolute;top:-30px;animation:sfall linear infinite;text-shadow:0 0 10px rgba(179,229,252,0.9);}}
        @keyframes sfall{{0%{{top:-30px;transform:translateX(0) rotate(0deg);}}50%{{transform:translateX(20px) rotate(180deg);}}100%{{top:110%;transform:translateX(-10px) rotate(360deg);}}}}
        </style>""", unsafe_allow_html=True)

    # 🌫️ FOG
    elif any(w in desc for w in ["fog","mist","haze","smoke","dust"]):
        st.markdown("""
        <style>.stApp{background:linear-gradient(180deg,#b0bec5 0%,#cfd8dc 50%,#eceff1 100%)!important;}</style>
        <div id="wbg"><div class="fog f1"></div><div class="fog f2"></div><div class="fog f3"></div></div>
        <style>
        #wbg{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-10;pointer-events:none;overflow:hidden;}
        .fog{position:absolute;width:220%;height:100px;left:-110%;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.3),transparent);border-radius:50%;animation:fdrift linear infinite;}
        .f1{top:20%;animation-duration:22s;}.f2{top:45%;animation-duration:28s;animation-delay:-10s;}.f3{top:70%;animation-duration:18s;animation-delay:-5s;}
        @keyframes fdrift{0%{transform:translateX(-20%);}100%{transform:translateX(20%);}}
        </style>""", unsafe_allow_html=True)

    # ☁️ CLOUDY — realistic multi-speed parallax layers
    else:
        cloud_data = [
            (3,  160, 48,  6,  0,   0.80),
            (13, 260, 70,  9,  -2,  0.88),
            (22, 200, 58,  7,  -1,  0.75),
            (32, 330, 85,  12, -5,  0.92),
            (42, 180, 52,  8,  -3,  0.78),
            (52, 280, 72,  10, -4,  0.85),
        ]
        clouds = ""
        for top, w, h, dur, delay, op in cloud_data:
            clouds += f'<div class="cc" style="top:{top}%;width:{w}px;height:{h}px;animation-duration:{dur}s;animation-delay:{delay}s;opacity:{op};"></div>'

        st.markdown(f"""
        <style>.stApp{{background:linear-gradient(180deg,#5BA3D9 0%,#74B9E8 28%,#A8D5F0 58%,#D0EAFB 82%,#EAF6FF 100%)!important;}}</style>
        <div id="wbg">{clouds}</div>
        <style>
        #wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-10;pointer-events:none;overflow:hidden;}}
        .cc{{position:absolute;left:-360px;
            background:rgba(255,255,255,0.90);
            border-radius:80px;
            box-shadow:0 6px 20px rgba(80,140,200,0.10),inset 0 -3px 8px rgba(180,220,255,0.15);
            animation:ccmove linear infinite;}}
        .cc::before{{content:'';position:absolute;top:-48%;left:16%;width:50%;height:135%;background:rgba(255,255,255,0.94);border-radius:50%;}}
        .cc::after{{content:'';position:absolute;top:-36%;left:50%;width:38%;height:112%;background:rgba(245,252,255,0.90);border-radius:50%;}}
        @keyframes ccmove{{0%{{left:-360px;}}100%{{left:110%;}}}}
        </style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  LIVE CLOCK
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="clock-bar">
    <div class="clock-time" id="liveclock">--:--:--</div>
    <div class="clock-date" id="livedate">Loading...</div>
</div>
<script>
function updateClock() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2,'0');
    const m = String(now.getMinutes()).padStart(2,'0');
    const s = String(now.getSeconds()).padStart(2,'0');
    document.getElementById('liveclock').textContent = h + ':' + m + ':' + s;
    const hour = now.getHours();
    let period, color, bg;
    if (hour >= 5 && hour < 12)       { period='🌅 Morning';   color='#7B3F00'; bg='rgba(255,200,80,0.25)'; }
    else if (hour >= 12 && hour < 17) { period='☀️ Afternoon'; color='#B34700'; bg='rgba(255,140,0,0.20)'; }
    else if (hour >= 17 && hour < 20) { period='🌇 Evening';   color='#7B0035'; bg='rgba(255,80,80,0.20)'; }
    else                               { period='🌙 Night';     color='#1a237e'; bg='rgba(30,60,180,0.20)'; }
    const days=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    const months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const dateStr = days[now.getDay()] + ', ' + now.getDate() + ' ' + months[now.getMonth()] + ' ' + now.getFullYear();
    document.getElementById('livedate').innerHTML = dateStr +
        ' &nbsp;<span class="day-badge" style="color:'+color+';background:'+bg+';border:1px solid '+color+'44;">'+period+'</span>';
}
updateClock();
setInterval(updateClock, 1000);
</script>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title"> ClimateIQ</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-Powered Weather Intelligence · Real-Time Analytics · LSTM Forecasting</div>', unsafe_allow_html=True)
st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── CITY INPUT ────────────────────────────────────────────────────────────────
col_inp, col_btn = st.columns([4, 1])
with col_inp:
    city = st.text_input("🏙️ Enter City Name", "Rajkot", placeholder="e.g. Mumbai, Delhi, London")
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    search = st.button("🔍 Analyze", use_container_width=True)

# ── MAIN LOGIC ────────────────────────────────────────────────────────────────
if city:
    with st.spinner(f"⚡ Fetching live data for **{city}**..."):
        weather_data = get_weather(city)

    if "cod" in weather_data and str(weather_data["cod"]) == "404":
        st.error(f"❌ City '{city}' not found.")
        st.stop()
    elif "error" in weather_data:
        st.error(f"❌ Network error: {weather_data['error']}")
        st.stop()
    elif "coord" not in weather_data:
        st.error("❌ API error. Check your OpenWeather API key in secrets.")
        st.stop()

    lat        = weather_data["coord"]["lat"]
    lon        = weather_data["coord"]["lon"]
    temp       = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    humidity   = weather_data["main"]["humidity"]
    wind       = weather_data["wind"]["speed"]
    pressure   = weather_data["main"]["pressure"]
    visibility = weather_data.get("visibility", 10000) / 1000
    description= weather_data["weather"][0]["description"].title()

    set_weather_background(description, temp)

    aqi_val, aqi_label, aqi_emoji = get_aqi(lat, lon)

    # ── METRIC CARDS ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-head">📊 LIVE CONDITIONS</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, label in [
        (c1, f"{temp:.1f}°C",       "🌡️ Temperature"),
        (c2, f"{feels_like:.1f}°C", "🤔 Feels Like"),
        (c3, f"{humidity}%",         "💧 Humidity"),
        (c4, f"{wind} m/s",          "🌪️ Wind Speed"),
        (c5, f"{visibility:.1f} km", "👁️ Visibility"),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-val">{val}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── STATUS + AQI + PRESSURE ───────────────────────────────────────────────
    col_desc, col_aqi, col_pres = st.columns(3)
    with col_desc:
        badge = "🔥 Hot Climate" if temp > 35 else ("❄️ Cold Climate" if temp < 10 else "🌤️ Comfortable")
        st.markdown(f'<div class="glass-card"><div style="font-size:1.3rem;font-weight:700;color:#002a5c;">{badge}</div><div style="color:#004a8f;font-size:0.85rem;margin-top:4px;">{description}</div></div>', unsafe_allow_html=True)
    with col_aqi:
        aqi_colors = {1:"#00897B",2:"#7CB342",3:"#F9A825",4:"#E64A19",5:"#6A1B9A"}
        ac = aqi_colors.get(aqi_val, "#555")
        st.markdown(f'<div class="glass-card"><div style="font-size:0.8rem;color:#004a8f;margin-bottom:6px;font-weight:600;">AIR QUALITY INDEX</div><span class="aqi-pill" style="background:{ac}22;color:{ac};border:1px solid {ac};">{aqi_emoji} {aqi_label} (AQI {aqi_val})</span></div>', unsafe_allow_html=True)
    with col_pres:
        st.markdown(f'<div class="glass-card"><div style="font-size:0.8rem;color:#004a8f;margin-bottom:4px;font-weight:600;">PRESSURE</div><div style="font-size:1.6rem;font-weight:700;color:#0055aa;">{pressure} hPa</div><div style="font-size:0.8rem;color:#004a8f;">{"🔻 Low" if pressure < 1010 else "🔺 Normal"}</div></div>', unsafe_allow_html=True)

    # ── ALERTS ────────────────────────────────────────────────────────────────
    alerts = generate_alerts(temp, humidity, wind, aqi_val)
    if alerts:
        st.markdown('<div class="section-head">⚠️ SMART ALERTS</div>', unsafe_allow_html=True)
        for alert_type, msg in alerts:
            st.markdown(f'<div class="alert-{alert_type}">{msg}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── MAP + FORECAST ────────────────────────────────────────────────────────
    map_col, chart_col = st.columns([1, 1])
    with map_col:
        st.markdown('<div class="section-head">📍 LOCATION MAP</div>', unsafe_allow_html=True)
        m = folium.Map(location=[lat, lon], zoom_start=10, tiles="OpenStreetMap")
        folium.Marker([lat, lon], popup=f"<b>{city}</b><br>{temp}°C · {description}", tooltip=city, icon=folium.Icon(color="blue", icon="cloud")).add_to(m)
        folium.Circle([lat, lon], radius=5000, color="#0077cc", fill=True, fill_opacity=0.1).add_to(m)
        st_folium(m, height=350, width=None)

    with chart_col:
        st.markdown('<div class="section-head">📈 5-DAY FORECAST</div>', unsafe_allow_html=True)
        with st.spinner("Loading forecast..."):
            forecast_data = get_forecast(city)
        if "list" in forecast_data:
            items = forecast_data["list"][:15]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[i["dt_txt"][5:16] for i in items],
                y=[i["main"]["temp"] for i in items],
                mode="lines+markers",
                line=dict(color="#0077cc", width=2.5),
                marker=dict(size=6, color="#FFD600"),
                fill="tozeroy", fillcolor="rgba(0,119,204,0.10)",
                name="Temperature °C",
            ))
            fig.update_layout(
                plot_bgcolor="rgba(255,255,255,0.45)", paper_bgcolor="rgba(255,255,255,0.30)",
                font=dict(color="#003366", size=11),
                xaxis=dict(gridcolor="rgba(0,80,160,0.15)", tickangle=-30),
                yaxis=dict(gridcolor="rgba(0,80,160,0.15)", title="°C"),
                margin=dict(t=10,b=10,l=10,r=10), height=350,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Could not load forecast data.")

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── LSTM ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-head">🧠 LSTM AI TEMPERATURE PREDICTION (Next 7 Days)</div>', unsafe_allow_html=True)
    with st.spinner("🤖 Training LSTM model..."):
        real_temps   = [i["main"]["temp"] for i in forecast_data["list"]] if "list" in forecast_data else []
        model        = train_model(real_temps)
        future_preds = predict_next(model, real_temps if real_temps else [temp], steps=7)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=[f"Day {i+1}" for i in range(7)], y=future_preds,
        marker=dict(color=future_preds, colorscale="RdYlGn_r", showscale=True,
                    colorbar=dict(title="°C", tickfont=dict(color="#003366"))),
        text=[f"{v:.1f}°C" for v in future_preds], textposition="outside",
        textfont=dict(color="#002a5c", size=12),
    ))
    fig2.update_layout(
        plot_bgcolor="rgba(255,255,255,0.45)", paper_bgcolor="rgba(255,255,255,0.30)",
        font=dict(color="#003366"),
        yaxis=dict(gridcolor="rgba(0,80,160,0.15)", title="Predicted Temp (°C)"),
        xaxis=dict(gridcolor="rgba(0,80,160,0.15)"),
        margin=dict(t=20,b=10,l=10,r=10), height=320,
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("⚡ LSTM model trained on live forecast data · Predictions are indicative")

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── CHATBOT ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-head">🤖 CLIMATEIQ AI ASSISTANT (Gemini)</div>', unsafe_allow_html=True)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    weather_ctx = {"city": city, "temp": temp, "humidity": humidity, "wind": wind}

    for role, msg in st.session_state.chat_history:
        css  = "chat-bubble-user" if role == "user" else "chat-bubble-ai"
        icon = "🧑" if role == "user" else "🤖"
        st.markdown(f'<div class="{css}">{icon} {msg}</div>', unsafe_allow_html=True)

    col_q, col_send = st.columns([5, 1])
    with col_q:
        user_q = st.text_input("Ask anything about weather, health, travel, climate...", key="chatbox", placeholder="e.g. Is it safe to travel today?")
    with col_send:
        st.markdown("<br>", unsafe_allow_html=True)
        send = st.button("Send 🚀", use_container_width=True)

    if send and user_q:
        st.session_state.chat_history.append(("user", user_q))
        with st.spinner("🤖 Thinking..."):
            answer = ask_ai(user_q, weather_ctx)
        st.session_state.chat_history.append(("ai", answer))
        st.rerun()

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#004a8f;font-size:0.8rem;font-weight:500;">ClimateIQ By Viren Solanki · Built with Streamlit + OpenWeatherMap + Gemini AI + TensorFlow LSTM</div>', unsafe_allow_html=True)
