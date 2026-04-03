import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from utils import get_weather, get_forecast
from aqi import get_aqi
from alerts import generate_alerts
from ml_lstm import train_model, predict_next
from chatbot import ask_ai

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClimateIQ Ultra",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0E1117;
    color: #FFFFFF;
}

/* Title */
.main-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.8rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(135deg, #00C9A7, #007FFF, #9B59B6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
    letter-spacing: 0.08em;
}
.sub-title {
    text-align: center;
    color: #888;
    font-size: 0.95rem;
    margin-bottom: 1.8rem;
    letter-spacing: 0.04em;
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(145deg, #1a1f2e, #141824);
    border: 1px solid #2a3350;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,201,167,0.08);
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-3px); }
.metric-val { font-size: 2rem; font-weight: 700; color: #00C9A7; }
.metric-label { font-size: 0.8rem; color: #888; margin-top: 4px; letter-spacing: 0.05em; }

/* Section headers */
.section-head {
    font-family: 'Orbitron', monospace;
    font-size: 1.1rem;
    color: #00C9A7;
    border-left: 4px solid #00C9A7;
    padding-left: 10px;
    margin: 24px 0 12px;
    letter-spacing: 0.04em;
}

/* Alert badges */
.alert-error   { background:#3d1a1a; border-left:4px solid #FF5252; padding:10px 16px; border-radius:8px; margin:6px 0; }
.alert-warning { background:#3d2d0e; border-left:4px solid #FFC107; padding:10px 16px; border-radius:8px; margin:6px 0; }
.alert-info    { background:#0e2840; border-left:4px solid #29B6F6; padding:10px 16px; border-radius:8px; margin:6px 0; }

/* AQI pill */
.aqi-pill {
    display:inline-block;
    padding:6px 18px;
    border-radius:999px;
    font-weight:700;
    font-size:1rem;
    margin-top:4px;
}

/* Chat */
.chat-bubble-user { background:#1a2a3a; padding:10px 16px; border-radius:12px 12px 0 12px; margin:6px 0; }
.chat-bubble-ai   { background:#192a22; padding:10px 16px; border-radius:12px 12px 12px 0; margin:6px 0; border-left:3px solid #00C9A7; }

/* Divider */
.fancy-divider { border:none; border-top:1px solid #1e2a40; margin:24px 0; }
</style>
""", unsafe_allow_html=True)
def set_weather_background(description, temp):
    desc = description.lower()

    # ☀️ SUNNY
    if any(w in desc for w in ["clear", "sunny"]):
        bg = """
        <style>
        .stApp {
            background: linear-gradient(180deg, #FF8C00 0%, #FFD700 40%, #87CEEB 100%);
        }
        </style>
        <div id="weather-bg">
            <div class="sun"></div>
            <div class="sun-ray r1"></div><div class="sun-ray r2"></div>
            <div class="sun-ray r3"></div><div class="sun-ray r4"></div>
            <div class="sun-ray r5"></div><div class="sun-ray r6"></div>
        </div>
        <style>
        #weather-bg { position:fixed; top:0; left:0; width:100%; height:100%; z-index:0; pointer-events:none; overflow:hidden; }
        .sun {
            position:absolute; top:60px; left:50%;
            width:120px; height:120px;
            background: radial-gradient(circle, #FFE500, #FF8C00);
            border-radius:50%;
            box-shadow: 0 0 80px 40px rgba(255,220,0,0.4);
            animation: pulse-sun 3s ease-in-out infinite;
        }
        @keyframes pulse-sun {
            0%,100% { box-shadow: 0 0 80px 40px rgba(255,220,0,0.4); }
            50% { box-shadow: 0 0 120px 60px rgba(255,200,0,0.6); }
        }
        .sun-ray {
            position:absolute; top:115px; left:calc(50% + 55px);
            width:80px; height:4px;
            background: rgba(255,230,0,0.7);
            border-radius:4px;
            transform-origin: -55px center;
            animation: spin-ray 8s linear infinite;
        }
        .r1{transform:rotate(0deg);}   .r2{transform:rotate(60deg);}
        .r3{transform:rotate(120deg);} .r4{transform:rotate(180deg);}
        .r5{transform:rotate(240deg);} .r6{transform:rotate(300deg);}
        @keyframes spin-ray { from{transform:rotate(var(--r,0deg));} to{transform:rotate(calc(var(--r,0deg) + 360deg));} }
        </style>
        """

    # 🌧️ RAIN
    elif any(w in desc for w in ["rain", "drizzle", "shower"]):
        drops = "".join([
            f'<div class="drop" style="left:{i*2.5}%;animation-delay:{(i*0.13)%2}s;animation-duration:{0.6+(i%5)*0.15}s;height:{10+(i%8)*3}px;opacity:{0.4+(i%5)*0.1};"></div>'
            for i in range(40)
        ])
        bg = f"""
        <style>
        .stApp {{
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        }}
        </style>
        <div id="weather-bg">
            {drops}
            <div class="lightning"></div>
        </div>
        <style>
        #weather-bg {{ position:fixed; top:0; left:0; width:100%; height:100%; z-index:0; pointer-events:none; overflow:hidden; }}
        .drop {{
            position:absolute; top:-20px; width:2px;
            background: linear-gradient(180deg, transparent, #89CFF0, #4FC3F7);
            border-radius:2px;
            animation: fall linear infinite;
        }}
        @keyframes fall {{
            0% {{ top:-20px; }}
            100% {{ top:110%; }}
        }}
        .lightning {{
            position:absolute; top:0; left:0; width:100%; height:100%;
            background: rgba(255,255,255,0);
            animation: lightning-flash 6s ease-in-out infinite;
        }}
        @keyframes lightning-flash {{
            0%,89%,91%,93%,100% {{ background:rgba(255,255,255,0); }}
            90%,92% {{ background:rgba(255,255,255,0.08); }}
        }}
        </style>
        """

    # ❄️ SNOW / COLD
    elif any(w in desc for w in ["snow", "blizzard", "sleet"]) or temp < 2:
        flakes = "".join([
            f'<div class="flake" style="left:{i*2.6}%;animation-delay:{(i*0.2)%4}s;animation-duration:{3+(i%4)}s;font-size:{10+(i%3)*6}px;opacity:{0.4+(i%4)*0.15};">❄</div>'
            for i in range(38)
        ])
        bg = f"""
        <style>
        .stApp {{
            background: linear-gradient(180deg, #0a0a1a 0%, #1a2a4a 50%, #2a4a6a 100%);
        }}
        </style>
        <div id="weather-bg">
            {flakes}
        </div>
        <style>
        #weather-bg {{ position:fixed; top:0; left:0; width:100%; height:100%; z-index:0; pointer-events:none; overflow:hidden; }}
        .flake {{
            position:absolute; top:-30px; color:#B0E0FF;
            animation: snowfall linear infinite;
            text-shadow: 0 0 8px rgba(176,224,255,0.8);
        }}
        @keyframes snowfall {{
            0% {{ top:-30px; transform:translateX(0) rotate(0deg); }}
            50% {{ transform:translateX(30px) rotate(180deg); }}
            100% {{ top:110%; transform:translateX(-20px) rotate(360deg); }}
        }}
        </style>
        """

    # 🌩️ THUNDERSTORM
    elif any(w in desc for w in ["thunder", "storm", "tornado"]):
        drops = "".join([
            f'<div class="drop" style="left:{i*2.5}%;animation-delay:{(i*0.1)%1.5}s;animation-duration:{0.4+(i%4)*0.1}s;height:{15+(i%6)*4}px;"></div>'
            for i in range(50)
        ])
        bg = f"""
        <style>
        .stApp {{
            background: linear-gradient(180deg, #0d0d0d 0%, #1a0a00 50%, #2d1a00 100%);
        }}
        </style>
        <div id="weather-bg">
            {drops}
            <div class="big-lightning"></div>
            <div class="storm-overlay"></div>
        </div>
        <style>
        #weather-bg {{ position:fixed; top:0; left:0; width:100%; height:100%; z-index:0; pointer-events:none; overflow:hidden; }}
        .drop {{
            position:absolute; top:-20px; width:2px;
            background: linear-gradient(180deg, transparent, #607D8B);
            border-radius:2px;
            animation: fall linear infinite;
        }}
        @keyframes fall {{
            0% {{ top:-20px; }} 100% {{ top:110%; }}
        }}
        .big-lightning {{
            position:absolute; top:0; left:0; width:100%; height:100%;
            animation: big-flash 3s ease-in-out infinite;
        }}
        @keyframes big-flash {{
            0%,79%,82%,85%,100% {{ background:rgba(255,255,255,0); }}
            80%,84% {{ background:rgba(255,200,100,0.12); }}
            81% {{ background:rgba(255,255,255,0.18); }}
        }}
        .storm-overlay {{
            position:absolute; top:0; left:0; width:100%; height:100%;
            background: radial-gradient(ellipse at 50% 0%, rgba(255,100,0,0.08) 0%, transparent 70%);
            animation: storm-pulse 2s ease-in-out infinite;
        }}
        @keyframes storm-pulse {{
            0%,100% {{ opacity:0.5; }} 50% {{ opacity:1; }}
        }}
        </style>
        """

    # 🌫️ FOG / MIST / HAZE
    elif any(w in desc for w in ["fog", "mist", "haze", "smoke", "dust"]):
        bg = """
        <style>
        .stApp {
            background: linear-gradient(180deg, #2a2a2a 0%, #3a3a3a 50%, #4a4a4a 100%);
        }
        </style>
        <div id="weather-bg">
            <div class="fog-layer f1"></div>
            <div class="fog-layer f2"></div>
            <div class="fog-layer f3"></div>
        </div>
        <style>
        #weather-bg { position:fixed; top:0; left:0; width:100%; height:100%; z-index:0; pointer-events:none; overflow:hidden; }
        .fog-layer {
            position:absolute; width:200%; height:120px;
            background: linear-gradient(90deg, transparent, rgba(200,200,200,0.15), transparent);
            border-radius:50%;
            animation: drift linear infinite;
        }
        .f1 { top:20%; animation-duration:18s; animation-delay:0s; }
        .f2 { top:45%; animation-duration:24s; animation-delay:-8s; opacity:0.7; }
        .f3 { top:70%; animation-duration:20s; animation-delay:-4s; opacity:0.5; }
        @keyframes drift {
            0% { transform:translateX(-50%); }
            100% { transform:translateX(0%); }
        }
        </style>
        """

    # ☁️ CLOUDY (default)
    else:
        clouds = "".join([
            f'<div class="cloud c{i}" style="top:{15+i*12}%;animation-duration:{20+i*5}s;animation-delay:-{i*4}s;opacity:{0.5+i*0.1};transform:scale({0.6+i*0.15});"></div>'
            for i in range(5)
        ])
        bg = f"""
        <style>
        .stApp {{
            background: linear-gradient(180deg, #1a1a2e 0%, #2d3561 50%, #1a2a4a 100%);
        }}
        </style>
        <div id="weather-bg">
            {clouds}
        </div>
        <style>
        #weather-bg {{ position:fixed; top:0; left:0; width:100%; height:100%; z-index:0; pointer-events:none; overflow:hidden; }}
        .cloud {{
            position:absolute; left:-200px; width:200px; height:60px;
            background: rgba(180,180,200,0.15);
            border-radius:50px;
            box-shadow: 0 0 40px rgba(180,180,200,0.1);
            animation: float-cloud linear infinite;
        }}
        .cloud::before {{
            content:''; position:absolute; top:-30px; left:40px;
            width:80px; height:60px;
            background: rgba(180,180,200,0.15);
            border-radius:50%;
        }}
        .cloud::after {{
            content:''; position:absolute; top:-20px; left:90px;
            width:60px; height:50px;
            background: rgba(180,180,200,0.12);
            border-radius:50%;
        }}
        @keyframes float-cloud {{
            0% {{ left:-250px; }} 100% {{ left:110%; }}
        }}
        </style>
        """

    st.markdown(bg, unsafe_allow_html=True)

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

    # ── Error Handling
    if "cod" in weather_data and str(weather_data["cod"]) == "404":
        st.error(f"❌ City **'{city}'** not found. Check spelling and try again.")
        st.stop()
    elif "error" in weather_data:
        st.error(f"❌ Network error: {weather_data['error']}")
        st.stop()
    elif "coord" not in weather_data:
        st.error("❌ Unexpected API response. Check your OpenWeather API key in secrets.")
        st.stop()

    # ── Extract Data
    lat = weather_data["coord"]["lat"]
    lon = weather_data["coord"]["lon"]
    temp = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    humidity = weather_data["main"]["humidity"]
    wind = weather_data["wind"]["speed"]
    pressure = weather_data["main"]["pressure"]
    visibility = weather_data.get("visibility", 10000) / 1000  # km
    description = weather_data["weather"][0]["description"].title()
    weather_icon = weather_data["weather"][0]["icon"]
set_weather_background(description, temp)
    # ── AQI
    aqi_val, aqi_label, aqi_emoji = get_aqi(lat, lon)

    # ─── METRIC CARDS ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-head">📊 LIVE CONDITIONS</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (c1, f"{temp:.1f}°C", "🌡️ Temperature"),
        (c2, f"{feels_like:.1f}°C", "🤔 Feels Like"),
        (c3, f"{humidity}%", "💧 Humidity"),
        (c4, f"{wind} m/s", "🌪️ Wind Speed"),
        (c5, f"{visibility:.1f} km", "👁️ Visibility"),
    ]
    for col, val, label in metrics:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-val">{val}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── CLIMATE STATUS BADGE ──────────────────────────────────────────────────
    col_desc, col_aqi, col_pres = st.columns(3)
    with col_desc:
        if temp > 35:
            badge = "🔥 Hot Climate"
            bg = "#3d1a1a"
        elif temp < 10:
            badge = "❄️ Cold Climate"
            bg = "#0e1d40"
        else:
            badge = "🌤️ Comfortable"
            bg = "#1a3020"
        st.markdown(f'<div style="background:{bg};border-radius:12px;padding:12px 16px;text-align:center;">'
                    f'<div style="font-size:1.3rem;font-weight:700;">{badge}</div>'
                    f'<div style="color:#888;font-size:0.85rem;">{description}</div></div>',
                    unsafe_allow_html=True)

    with col_aqi:
        aqi_colors = {1: "#00C9A7", 2: "#A8D08D", 3: "#FFC107", 4: "#FF7043", 5: "#E040FB"}
        aqi_color = aqi_colors.get(aqi_val, "#888")
        st.markdown(
            f'<div style="background:#1a1f2e;border-radius:12px;padding:12px 16px;text-align:center;">'
            f'<div style="font-size:0.8rem;color:#888;margin-bottom:4px;">AIR QUALITY INDEX</div>'
            f'<span class="aqi-pill" style="background:{aqi_color}22;color:{aqi_color};border:1px solid {aqi_color};">'
            f'{aqi_emoji} {aqi_label} (AQI {aqi_val})</span></div>',
            unsafe_allow_html=True
        )

    with col_pres:
        st.markdown(
            f'<div style="background:#1a1f2e;border-radius:12px;padding:12px 16px;text-align:center;">'
            f'<div style="font-size:0.8rem;color:#888;margin-bottom:4px;">PRESSURE</div>'
            f'<div style="font-size:1.6rem;font-weight:700;color:#007FFF;">{pressure} hPa</div>'
            f'<div style="font-size:0.8rem;color:#888;">{"🔻 Low" if pressure < 1010 else "🔺 Normal"}</div></div>',
            unsafe_allow_html=True
        )

    # ─── ALERTS ────────────────────────────────────────────────────────────────
    alerts = generate_alerts(temp, humidity, wind, aqi_val)
    if alerts:
        st.markdown('<div class="section-head">⚠️ SMART ALERTS</div>', unsafe_allow_html=True)
        for alert_type, msg in alerts:
            st.markdown(f'<div class="alert-{alert_type}">{msg}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ─── MAP + FORECAST (side by side) ────────────────────────────────────────
    map_col, chart_col = st.columns([1, 1])

    with map_col:
        st.markdown('<div class="section-head">📍 LOCATION MAP</div>', unsafe_allow_html=True)
        m = folium.Map(location=[lat, lon], zoom_start=10, tiles="OpenStreetMap")
        folium.Marker(
            [lat, lon],
            popup=f"<b>{city}</b><br>{temp}°C · {description}",
            tooltip=city,
            icon=folium.Icon(color="green", icon="cloud"),
        ).add_to(m)
        folium.Circle(
            [lat, lon],
            radius=5000,
            color="#00C9A7",
            fill=True,
            fill_opacity=0.1,
        ).add_to(m)
        st_folium(m, height=350, width=None)

    with chart_col:
        st.markdown('<div class="section-head">📈 5-DAY FORECAST</div>', unsafe_allow_html=True)
        with st.spinner("Loading forecast..."):
            forecast_data = get_forecast(city)

        if "list" in forecast_data:
            items = forecast_data["list"][:15]
            f_temps = [i["main"]["temp"] for i in items]
            f_times = [i["dt_txt"][5:16] for i in items]  # MM-DD HH:MM

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=f_times, y=f_temps,
                mode="lines+markers",
                line=dict(color="#00C9A7", width=2.5),
                marker=dict(size=6, color="#007FFF"),
                fill="tozeroy",
                fillcolor="rgba(0,201,167,0.08)",
                name="Temperature °C",
            ))
            fig.update_layout(
                plot_bgcolor="#141824",
                paper_bgcolor="#141824",
                font=dict(color="#888", size=11),
                xaxis=dict(gridcolor="#1e2a40", tickangle=-30),
                yaxis=dict(gridcolor="#1e2a40", title="°C"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=350,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Could not load forecast data.")

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ─── LSTM AI PREDICTION ───────────────────────────────────────────────────
    st.markdown('<div class="section-head">🧠 LSTM AI TEMPERATURE PREDICTION (Next 7 Days)</div>', unsafe_allow_html=True)

    with st.spinner("🤖 Training LSTM model..."):
        # Use real forecast temps as training data
        if "list" in forecast_data:
            real_temps = [i["main"]["temp"] for i in forecast_data["list"]]
        else:
            real_temps = []

        model = train_model(real_temps)
        future_preds = predict_next(model, real_temps if real_temps else [temp], steps=7)

    day_labels = [f"Day {i+1}" for i in range(7)]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=day_labels,
        y=future_preds,
        marker=dict(
            color=future_preds,
            colorscale="RdYlGn_r",
            showscale=True,
            colorbar=dict(title="°C", tickfont=dict(color="#888")),
        ),
        text=[f"{v:.1f}°C" for v in future_preds],
        textposition="outside",
        textfont=dict(color="#FFFFFF", size=12),
    ))
    fig2.update_layout(
        plot_bgcolor="#141824",
        paper_bgcolor="#141824",
        font=dict(color="#888"),
        yaxis=dict(gridcolor="#1e2a40", title="Predicted Temp (°C)"),
        xaxis=dict(gridcolor="#1e2a40"),
        margin=dict(t=20, b=10, l=10, r=10),
        height=320,
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("⚡ LSTM model trained on live forecast data · Predictions are indicative")

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

   # ─── AI CHATBOT ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-head">🤖 CLIMATEIQ AI ASSISTANT (Gemini)</div>', unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

weather_ctx = {
    "city": city, "temp": temp, "humidity": humidity, "wind": wind
}

for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f'<div class="chat-bubble-user">🧑 {msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-ai">🤖 {msg}</div>', unsafe_allow_html=True)

col_q, col_send = st.columns([5, 1])
with col_q:
    user_q = st.text_input(
        "Ask anything about weather, health, travel, climate...",
        key="chatbox",
        placeholder="e.g. Is it safe to travel today?"
    )
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

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;color:#444;font-size:0.8rem;">'
    'ClimateIQ ULTRA · Built with Streamlit + OpenWeatherMap + Gemini AI + TensorFlow LSTM'
    '</div>',
    unsafe_allow_html=True
)
