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
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #FFFFFF; }
.main-title { font-family:'Orbitron',monospace; font-size:2.8rem; font-weight:700; text-align:center; background:linear-gradient(135deg,#00C9A7,#007FFF,#9B59B6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:0.2rem; letter-spacing:0.08em; }
.sub-title { text-align:center; color:#ccc; font-size:0.95rem; margin-bottom:1.8rem; letter-spacing:0.04em; }
.metric-card { background:rgba(26,31,46,0.85); border:1px solid #2a3350; border-radius:16px; padding:20px; text-align:center; box-shadow:0 4px 24px rgba(0,201,167,0.08); transition:transform 0.2s; backdrop-filter:blur(8px); }
.metric-card:hover { transform:translateY(-3px); }
.metric-val { font-size:2rem; font-weight:700; color:#00C9A7; }
.metric-label { font-size:0.8rem; color:#aaa; margin-top:4px; letter-spacing:0.05em; }
.section-head { font-family:'Orbitron',monospace; font-size:1.1rem; color:#00C9A7; border-left:4px solid #00C9A7; padding-left:10px; margin:24px 0 12px; letter-spacing:0.04em; }
.alert-error   { background:rgba(61,26,26,0.9); border-left:4px solid #FF5252; padding:10px 16px; border-radius:8px; margin:6px 0; }
.alert-warning { background:rgba(61,45,14,0.9); border-left:4px solid #FFC107; padding:10px 16px; border-radius:8px; margin:6px 0; }
.alert-info    { background:rgba(14,40,64,0.9); border-left:4px solid #29B6F6; padding:10px 16px; border-radius:8px; margin:6px 0; }
.aqi-pill { display:inline-block; padding:6px 18px; border-radius:999px; font-weight:700; font-size:1rem; margin-top:4px; }
.chat-bubble-user { background:rgba(26,42,58,0.9); padding:10px 16px; border-radius:12px 12px 0 12px; margin:6px 0; }
.chat-bubble-ai   { background:rgba(25,42,34,0.9); padding:10px 16px; border-radius:12px 12px 12px 0; margin:6px 0; border-left:3px solid #00C9A7; }
.fancy-divider { border:none; border-top:1px solid rgba(30,42,64,0.8); margin:24px 0; }
</style>
""", unsafe_allow_html=True)


def set_weather_background(description, temp):
    desc = description.lower()
    if any(w in desc for w in ["clear", "sunny"]):

        if "bg_set" not in st.session_state:
            st.session_state.bg_set = True

            st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(180deg,#FF6B00 0%,#FF9800 40%,#FFD54F 70%,#87CEEB 100%) !important;
            }

            #wbg {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                overflow: hidden;
                pointer-events: none;
            }

            /* ☀️ Sun (static) */
            .sun {
                position: absolute;
                top: 60px;
                right: 80px;
                width: 110px;
                height: 110px;
                border-radius: 50%;
                background: radial-gradient(circle, #FFF176, #FFD600, #FF8F00);
                box-shadow:
                    0 0 50px 25px rgba(255,214,0,0.5),
                    0 0 100px 50px rgba(255,152,0,0.3);
            }

            /* ☁️ Common cloud */
            .cloud {
                position: absolute;
                background: white;
                border-radius: 50px;
            }

            .cloud:before, .cloud:after {
                content: "";
                position: absolute;
                background: white;
                border-radius: 50%;
            }

            /* 🌫️ FAR CLOUD (slowest, small, light) */
            .cloud-far {
                width: 90px;
                height: 35px;
                top: 90px;
                left: -150px;
                opacity: 0.5;
                animation: cloudSlow 80s linear infinite;
            }
            .cloud-far:before { width: 40px; height: 40px; top: -15px; left: 10px; }
            .cloud-far:after  { width: 50px; height: 50px; top: -20px; right: 10px; }

            /* 🌥️ MID CLOUD */
            .cloud-mid {
                width: 140px;
                height: 50px;
                top: 160px;
                left: -250px;
                opacity: 0.7;
                animation: cloudMid 50s linear infinite;
            }
            .cloud-mid:before { width: 60px; height: 60px; top: -20px; left: 20px; }
            .cloud-mid:after  { width: 80px; height: 80px; top: -30px; right: 15px; }

            /* ☁️ NEAR CLOUD (fastest, big, bold) */
            .cloud-near {
                width: 200px;
                height: 70px;
                top: 230px;
                left: -350px;
                opacity: 0.9;
                animation: cloudFast 30s linear infinite;
            }
            .cloud-near:before { width: 80px; height: 80px; top: -25px; left: 30px; }
            .cloud-near:after  { width: 100px; height: 100px; top: -35px; right: 25px; }

            /* 🎯 Smooth continuous movement */
            @keyframes cloudSlow {
                from { transform: translateX(0); }
                to { transform: translateX(120vw); }
            }

            @keyframes cloudMid {
                from { transform: translateX(0); }
                to { transform: translateX(130vw); }
            }

            @keyframes cloudFast {
                from { transform: translateX(0); }
                to { transform: translateX(140vw); }
            }

            </style>

            <div id="wbg">
                <div class="sun"></div>

                <div class="cloud cloud-far"></div>
                <div class="cloud cloud-mid"></div>
                <div class="cloud cloud-near"></div>
            </div>
            """, unsafe_allow_html=True)
        
    elif any(w in desc for w in ["thunder", "storm", "tornado"]):
        drops = "".join([f'<div class="hd" style="left:{i*2}%;animation-delay:{round((i*0.08)%1.5,2)}s;animation-duration:{round(0.3+(i%4)*0.1,2)}s;height:{15+(i%6)*4}px;"></div>' for i in range(50)])
        st.markdown(f"""
        <style>.stApp{{background:linear-gradient(180deg,#050505 0%,#1a0800 40%,#2d1000 100%)!important;}}</style>
        <div id="wbg">{drops}<div class="bflash"></div><div class="sglow"></div></div>
        <style>
        #wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;}}
        .hd{{position:absolute;top:-20px;width:2px;background:linear-gradient(180deg,transparent,#78909C);border-radius:2px;animation:hfall linear infinite;}}
        @keyframes hfall{{0%{{top:-20px;}}100%{{top:110%;}}}}
        .bflash{{position:absolute;top:0;left:0;width:100%;height:100%;animation:blight 4s ease-in-out infinite;}}
        @keyframes blight{{0%,78%,83%,86%,100%{{background:rgba(255,255,255,0);}}79%,82%{{background:rgba(255,220,100,0.1);}}80%{{background:rgba(255,255,255,0.2);}}85%{{background:rgba(255,200,50,0.08);}}}}
        .sglow{{position:absolute;bottom:0;left:0;width:100%;height:40%;background:radial-gradient(ellipse at 50% 100%,rgba(255,80,0,0.12) 0%,transparent 70%);animation:sgp 2s ease-in-out infinite;}}
        @keyframes sgp{{0%,100%{{opacity:0.5;}}50%{{opacity:1;}}}}
        </style>""", unsafe_allow_html=True)

    elif any(w in desc for w in ["rain", "drizzle", "shower"]):
        drops = "".join([f'<div class="rd" style="left:{i*2.5}%;animation-delay:{round((i*0.13)%2.0,2)}s;animation-duration:{round(0.5+(i%6)*0.12,2)}s;height:{8+(i%8)*3}px;opacity:{round(0.3+(i%5)*0.12,2)};"></div>' for i in range(40)])
        st.markdown(f"""
        <style>.stApp{{background:linear-gradient(180deg,#0d1b2a 0%,#1a2f4a 50%,#0f2a3d 100%)!important;}}</style>
        <div id="wbg">{drops}<div class="loverlay"></div></div>
        <style>
        #wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;}}
        .rd{{position:absolute;top:-20px;width:2px;background:linear-gradient(180deg,transparent,#81D4FA,#4FC3F7);border-radius:2px;animation:rfall linear infinite;}}
        @keyframes rfall{{0%{{top:-20px;}}100%{{top:110%;}}}}
        .loverlay{{position:absolute;top:0;left:0;width:100%;height:100%;animation:lflash 7s ease-in-out infinite;}}
        @keyframes lflash{{0%,88%,92%,100%{{background:rgba(255,255,255,0);}}89%,91%{{background:rgba(255,255,255,0.07);}}90%{{background:rgba(200,230,255,0.12);}}}}
        </style>""", unsafe_allow_html=True)

    elif any(w in desc for w in ["snow", "blizzard", "sleet"]) or temp < 2:
        flakes = "".join([f'<div class="sf" style="left:{i*2.7}%;animation-delay:{round((i*0.18)%5,2)}s;animation-duration:{round(3+(i%5),2)}s;font-size:{8+(i%4)*5}px;opacity:{round(0.4+(i%4)*0.15,2)};color:#B3E5FC;">❄</div>' for i in range(37)])
        st.markdown(f"""
        <style>.stApp{{background:linear-gradient(180deg,#050a1a 0%,#0a1628 50%,#1a2a40 100%)!important;}}</style>
        <div id="wbg">{flakes}</div>
        <style>
        #wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;}}
        .sf{{position:absolute;top:-30px;animation:sfall linear infinite;text-shadow:0 0 10px rgba(179,229,252,0.9);}}
        @keyframes sfall{{0%{{top:-30px;transform:translateX(0) rotate(0deg);}}33%{{transform:translateX(20px) rotate(120deg);}}66%{{transform:translateX(-15px) rotate(240deg);}}100%{{top:110%;transform:translateX(10px) rotate(360deg);}}}}
        </style>""", unsafe_allow_html=True)

    elif any(w in desc for w in ["fog", "mist", "haze", "smoke", "dust"]):
        st.markdown("""
        <style>.stApp{background:linear-gradient(180deg,#1a1a1a 0%,#2d2d2d 50%,#3a3a3a 100%)!important;}</style>
        <div id="wbg"><div class="fog f1"></div><div class="fog f2"></div><div class="fog f3"></div><div class="fog f4"></div></div>
        <style>
        #wbg{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;}
        .fog{position:absolute;width:220%;height:100px;left:-110%;background:linear-gradient(90deg,transparent 0%,rgba(200,200,200,0.12) 30%,rgba(200,200,200,0.18) 50%,rgba(200,200,200,0.12) 70%,transparent 100%);border-radius:50%;animation:fdrift linear infinite;}
        .f1{top:15%;animation-duration:22s;}.f2{top:35%;animation-duration:28s;animation-delay:-10s;opacity:0.8;}.f3{top:55%;animation-duration:18s;animation-delay:-5s;opacity:0.6;}.f4{top:75%;animation-duration:32s;animation-delay:-15s;opacity:0.5;}
        @keyframes fdrift{0%{transform:translateX(-20%);}100%{transform:translateX(20%);}}
        </style>""", unsafe_allow_html=True)

    else:
        clouds = "".join([f'<div class="cl" style="top:{10+i*15}%;width:{160+i*40}px;height:{50+i*10}px;animation-duration:{18+i*6}s;animation-delay:-{i*5}s;opacity:{0.4+i*0.1};"></div>' for i in range(5)])
        st.markdown(f"""
        <style>.stApp{{background:linear-gradient(180deg,#0a0e1a 0%,#1a2040 50%,#0d1530 100%)!important;}}</style>
        <div id="wbg">{clouds}</div>
        <style>
        #wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;}}
        .cl{{position:absolute;left:-250px;background:rgba(160,170,200,0.15);border-radius:50px;box-shadow:0 0 30px rgba(160,170,200,0.08);animation:clfloat linear infinite;}}
        .cl::before{{content:'';position:absolute;top:-40%;left:20%;width:50%;height:120%;background:rgba(160,170,200,0.12);border-radius:50%;}}
        .cl::after{{content:'';position:absolute;top:-30%;left:50%;width:40%;height:100%;background:rgba(160,170,200,0.10);border-radius:50%;}}
        @keyframes clfloat{{0%{{left:-250px;}}100%{{left:110%;}}}}
        </style>""", unsafe_allow_html=True)


# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🌍 ClimateIQ ULTRA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-Powered Weather Intelligence · Real-Time Analytics · LSTM Forecasting</div>', unsafe_allow_html=True)
st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ─── CITY INPUT ────────────────────────────────────────────────────────────────
col_inp, col_btn = st.columns([4, 1])
with col_inp:
    city = st.text_input("🏙️ Enter City Name", "Rajkot", placeholder="e.g. Mumbai, Delhi, London")
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    search = st.button("🔍 Analyze", use_container_width=True)

# ─── MAIN LOGIC ────────────────────────────────────────────────────────────────
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

    lat = weather_data["coord"]["lat"]
    lon = weather_data["coord"]["lon"]
    temp = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    humidity = weather_data["main"]["humidity"]
    wind = weather_data["wind"]["speed"]
    pressure = weather_data["main"]["pressure"]
    visibility = weather_data.get("visibility", 10000) / 1000
    description = weather_data["weather"][0]["description"].title()

    set_weather_background(description, temp)

    aqi_val, aqi_label, aqi_emoji = get_aqi(lat, lon)

    st.markdown('<div class="section-head">📊 LIVE CONDITIONS</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, label in [
        (c1, f"{temp:.1f}°C", "🌡️ Temperature"),
        (c2, f"{feels_like:.1f}°C", "🤔 Feels Like"),
        (c3, f"{humidity}%", "💧 Humidity"),
        (c4, f"{wind} m/s", "🌪️ Wind Speed"),
        (c5, f"{visibility:.1f} km", "👁️ Visibility"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_desc, col_aqi, col_pres = st.columns(3)
    with col_desc:
        badge = "🔥 Hot Climate" if temp > 35 else ("❄️ Cold Climate" if temp < 10 else "🌤️ Comfortable")
        st.markdown(f'<div style="background:rgba(26,26,26,0.85);border-radius:12px;padding:12px 16px;text-align:center;backdrop-filter:blur(8px);"><div style="font-size:1.3rem;font-weight:700;">{badge}</div><div style="color:#aaa;font-size:0.85rem;">{description}</div></div>', unsafe_allow_html=True)

    with col_aqi:
        aqi_colors = {1:"#00C9A7",2:"#A8D08D",3:"#FFC107",4:"#FF7043",5:"#E040FB"}
        ac = aqi_colors.get(aqi_val, "#888")
        st.markdown(f'<div style="background:rgba(26,31,46,0.85);border-radius:12px;padding:12px 16px;text-align:center;backdrop-filter:blur(8px);"><div style="font-size:0.8rem;color:#aaa;margin-bottom:4px;">AIR QUALITY INDEX</div><span class="aqi-pill" style="background:{ac}22;color:{ac};border:1px solid {ac};">{aqi_emoji} {aqi_label} (AQI {aqi_val})</span></div>', unsafe_allow_html=True)

    with col_pres:
        st.markdown(f'<div style="background:rgba(26,31,46,0.85);border-radius:12px;padding:12px 16px;text-align:center;backdrop-filter:blur(8px);"><div style="font-size:0.8rem;color:#aaa;margin-bottom:4px;">PRESSURE</div><div style="font-size:1.6rem;font-weight:700;color:#007FFF;">{pressure} hPa</div><div style="font-size:0.8rem;color:#aaa;">{"🔻 Low" if pressure < 1010 else "🔺 Normal"}</div></div>', unsafe_allow_html=True)

    alerts = generate_alerts(temp, humidity, wind, aqi_val)
    if alerts:
        st.markdown('<div class="section-head">⚠️ SMART ALERTS</div>', unsafe_allow_html=True)
        for alert_type, msg in alerts:
            st.markdown(f'<div class="alert-{alert_type}">{msg}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    map_col, chart_col = st.columns([1, 1])
    with map_col:
        st.markdown('<div class="section-head">📍 LOCATION MAP</div>', unsafe_allow_html=True)
        m = folium.Map(location=[lat, lon], zoom_start=10, tiles="OpenStreetMap")
        folium.Marker([lat, lon], popup=f"<b>{city}</b><br>{temp}°C · {description}", tooltip=city, icon=folium.Icon(color="green", icon="cloud")).add_to(m)
        folium.Circle([lat, lon], radius=5000, color="#00C9A7", fill=True, fill_opacity=0.1).add_to(m)
        st_folium(m, height=350, width=None)

    with chart_col:
        st.markdown('<div class="section-head">📈 5-DAY FORECAST</div>', unsafe_allow_html=True)
        with st.spinner("Loading forecast..."):
            forecast_data = get_forecast(city)
        if "list" in forecast_data:
            items = forecast_data["list"][:15]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[i["dt_txt"][5:16] for i in items], y=[i["main"]["temp"] for i in items], mode="lines+markers", line=dict(color="#00C9A7", width=2.5), marker=dict(size=6, color="#007FFF"), fill="tozeroy", fillcolor="rgba(0,201,167,0.08)", name="Temperature °C"))
            fig.update_layout(plot_bgcolor="rgba(20,24,36,0.9)", paper_bgcolor="rgba(20,24,36,0.9)", font=dict(color="#888", size=11), xaxis=dict(gridcolor="#1e2a40", tickangle=-30), yaxis=dict(gridcolor="#1e2a40", title="°C"), margin=dict(t=10,b=10,l=10,r=10), height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Could not load forecast data.")

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    st.markdown('<div class="section-head">🧠 LSTM AI TEMPERATURE PREDICTION (Next 7 Days)</div>', unsafe_allow_html=True)
    with st.spinner("🤖 Training LSTM model..."):
        real_temps = [i["main"]["temp"] for i in forecast_data["list"]] if "list" in forecast_data else []
        model = train_model(real_temps)
        future_preds = predict_next(model, real_temps if real_temps else [temp], steps=7)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=[f"Day {i+1}" for i in range(7)], y=future_preds, marker=dict(color=future_preds, colorscale="RdYlGn_r", showscale=True, colorbar=dict(title="°C", tickfont=dict(color="#888"))), text=[f"{v:.1f}°C" for v in future_preds], textposition="outside", textfont=dict(color="#FFFFFF", size=12)))
    fig2.update_layout(plot_bgcolor="rgba(20,24,36,0.9)", paper_bgcolor="rgba(20,24,36,0.9)", font=dict(color="#888"), yaxis=dict(gridcolor="#1e2a40", title="Predicted Temp (°C)"), xaxis=dict(gridcolor="#1e2a40"), margin=dict(t=20,b=10,l=10,r=10), height=320)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("⚡ LSTM model trained on live forecast data · Predictions are indicative")

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    st.markdown('<div class="section-head">🤖 CLIMATEIQ AI ASSISTANT (Gemini)</div>', unsafe_allow_html=True)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    weather_ctx = {"city": city, "temp": temp, "humidity": humidity, "wind": wind}

    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f'<div class="chat-bubble-user">🧑 {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-ai">🤖 {msg}</div>', unsafe_allow_html=True)

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

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#666;font-size:0.8rem;">ClimateIQ By Viren Solanki· Built with Streamlit + OpenWeatherMap + Gemini AI + TensorFlow LSTM</div>', unsafe_allow_html=True)
