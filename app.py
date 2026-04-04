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
.sub-title { text-align:center; color:#e0f0ff; font-size:0.95rem; margin-bottom:1.8rem; letter-spacing:0.04em; text-shadow:0 1px 4px rgba(0,0,0,0.3); }
.metric-card { background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.35); border-radius:20px; padding:20px; text-align:center; box-shadow:0 8px 32px rgba(0,0,0,0.12); transition:transform 0.2s; backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); }
.metric-card:hover { transform:translateY(-4px); box-shadow:0 12px 40px rgba(0,0,0,0.18); }
.metric-val { font-size:2rem; font-weight:700; color:#003d7a; text-shadow:0 1px 2px rgba(255,255,255,0.5); }
.metric-label { font-size:0.8rem; color:#004a8f; margin-top:4px; letter-spacing:0.05em; font-weight:600; }
.section-head { font-family:'Orbitron',monospace; font-size:1.05rem; color:#003d7a; border-left:4px solid #0077cc; padding-left:10px; margin:24px 0 12px; letter-spacing:0.04em; text-shadow:0 1px 2px rgba(255,255,255,0.4); }
.alert-error   { background:rgba(255,80,80,0.2); border-left:4px solid #FF5252; padding:10px 16px; border-radius:10px; margin:6px 0; backdrop-filter:blur(8px); color:#fff; text-shadow:0 1px 2px rgba(0,0,0,0.4); }
.alert-warning { background:rgba(255,193,7,0.2); border-left:4px solid #FFC107; padding:10px 16px; border-radius:10px; margin:6px 0; backdrop-filter:blur(8px); color:#fff; text-shadow:0 1px 2px rgba(0,0,0,0.4); }
.alert-info    { background:rgba(41,182,246,0.2); border-left:4px solid #29B6F6; padding:10px 16px; border-radius:10px; margin:6px 0; backdrop-filter:blur(8px); color:#fff; text-shadow:0 1px 2px rgba(0,0,0,0.4); }
.aqi-pill { display:inline-block; padding:6px 18px; border-radius:999px; font-weight:700; font-size:1rem; margin-top:4px; }
.glass-card { background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.35); border-radius:16px; padding:14px 18px; text-align:center; backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); box-shadow:0 4px 20px rgba(0,0,0,0.1); }
.chat-bubble-user { background:rgba(255,255,255,0.22); border:1px solid rgba(255,255,255,0.3); padding:10px 16px; border-radius:16px 16px 0 16px; margin:6px 0; backdrop-filter:blur(8px); color:#002a5c; font-weight:500; }
.chat-bubble-ai   { background:rgba(0,100,200,0.15); border:1px solid rgba(0,150,255,0.3); padding:10px 16px; border-radius:16px 16px 16px 0; margin:6px 0; backdrop-filter:blur(8px); border-left:3px solid #0077cc; color:#001a3a; }
.fancy-divider { border:none; border-top:1px solid rgba(255,255,255,0.3); margin:24px 0; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  WEATHER BACKGROUND FUNCTION
# ══════════════════════════════════════════════════════════════════════════════
def set_weather_background(description, temp):
    desc = description.lower()

    # ─── ☀️ CLEAR / SUNNY — Sky Blue + Bright Sun + Moving Clouds ─────────────
    if any(w in desc for w in ["clear", "sunny"]) or (
        not any(w in desc for w in ["rain","drizzle","shower","thunder","storm","snow","blizzard","sleet","fog","mist","haze","smoke","dust","cloud"])
    ):
        clouds = "".join([
            f'<div class="dc" style="top:{8+i*11}%;width:{200+i*60}px;height:{60+i*15}px;'
            f'animation-duration:{22+i*8}s;animation-delay:-{i*7}s;opacity:{0.82+i*0.03};"></div>'
            for i in range(4)
        ])
        st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(180deg,
                #4FC3F7 0%,
                #81D4FA 25%,
                #B3E5FC 55%,
                #E1F5FE 80%,
                #f0faff 100%) !important;
        }}
        </style>
        <div id="wbg">
            <div class="dsun"></div>
            <div class="dray dr1"></div><div class="dray dr2"></div>
            <div class="dray dr3"></div><div class="dray dr4"></div>
            <div class="dray dr5"></div><div class="dray dr6"></div>
            {clouds}
        </div>
        <style>
        #wbg {{ position:fixed; top:0; left:0; width:100%; height:100%; z-index:0; pointer-events:none; overflow:hidden; }}

        /* ── Sun ── */
        .dsun {{
            position:absolute; top:35px; right:100px;
            width:110px; height:110px;
            background: radial-gradient(circle, #FFFDE7 10%, #FFE57F 40%, #FFD600 70%, #FFB300 100%);
            border-radius: 50%;
            box-shadow:
                0 0 0 15px rgba(255,230,80,0.15),
                0 0 0 30px rgba(255,200,0,0.10),
                0 0 60px 20px rgba(255,210,0,0.35),
                0 0 100px 40px rgba(255,180,0,0.15);
            animation: sunpulse 4s ease-in-out infinite;
        }}
        @keyframes sunpulse {{
            0%,100% {{ box-shadow: 0 0 0 15px rgba(255,230,80,0.15), 0 0 0 30px rgba(255,200,0,0.10), 0 0 60px 20px rgba(255,210,0,0.35), 0 0 100px 40px rgba(255,180,0,0.15); }}
            50%      {{ box-shadow: 0 0 0 20px rgba(255,230,80,0.20), 0 0 0 40px rgba(255,200,0,0.12), 0 0 80px 30px rgba(255,210,0,0.50), 0 0 130px 55px rgba(255,180,0,0.20); }}
        }}

        /* ── Sun Rays ── */
        .dray {{
            position:absolute; top:88px; right:145px;
            width:80px; height:4px;
            background: linear-gradient(90deg, rgba(255,230,50,0.85), transparent);
            border-radius: 4px;
            transform-origin: right center;
            animation: rayspin 12s linear infinite;
        }}
        .dr1 {{ transform:rotate(0deg);   }}
        .dr2 {{ transform:rotate(60deg);  }}
        .dr3 {{ transform:rotate(120deg); }}
        .dr4 {{ transform:rotate(180deg); }}
        .dr5 {{ transform:rotate(240deg); }}
        .dr6 {{ transform:rotate(300deg); }}
        @keyframes rayspin {{
            from {{ transform: rotate(var(--r,0deg)); }}
            to   {{ transform: rotate(calc(var(--r,0deg) + 360deg)); }}
        }}

        /* ── Clouds ── */
        .dc {{
            position:absolute; left:-320px;
            background: rgba(255,255,255,0.92);
            border-radius: 80px;
            box-shadow: 0 6px 24px rgba(100,160,220,0.15), inset 0 -4px 12px rgba(180,220,255,0.2);
            animation: cloudmove linear infinite;
        }}
        .dc::before {{
            content:''; position:absolute;
            top:-50%; left:15%;
            width:52%; height:140%;
            background: rgba(255,255,255,0.95);
            border-radius: 50%;
        }}
        .dc::after {{
            content:''; position:absolute;
            top:-38%; left:48%;
            width:40%; height:115%;
            background: rgba(245,252,255,0.90);
            border-radius: 50%;
        }}
        @keyframes cloudmove {{ 0% {{ left:-320px; }} 100% {{ left:110%; }} }}
        </style>
        """, unsafe_allow_html=True)

    # ─── ⛈️ THUNDERSTORM ──────────────────────────────────────────────────────
    elif any(w in desc for w in ["thunder", "storm", "tornado"]):
        drops = "".join([
            f'<div class="hd" style="left:{i*2}%;animation-delay:{round((i*0.08)%1.5,2)}s;animation-duration:{round(0.3+(i%4)*0.1,2)}s;height:{15+(i%6)*4}px;"></div>'
            for i in range(50)
        ])
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

    # ─── 🌧️ RAIN ──────────────────────────────────────────────────────────────
    elif any(w in desc for w in ["rain", "drizzle", "shower"]):
        drops = "".join([
            f'<div class="rd" style="left:{i*2.5}%;animation-delay:{round((i*0.13)%2.0,2)}s;animation-duration:{round(0.5+(i%6)*0.12,2)}s;height:{8+(i%8)*3}px;opacity:{round(0.3+(i%5)*0.12,2)};"></div>'
            for i in range(40)
        ])
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

    # ─── ❄️ SNOW ──────────────────────────────────────────────────────────────
    elif any(w in desc for w in ["snow", "blizzard", "sleet"]) or temp < 2:
        flakes = "".join([
            f'<div class="sf" style="left:{i*2.7}%;animation-delay:{round((i*0.18)%5,2)}s;animation-duration:{round(3+(i%5),2)}s;font-size:{8+(i%4)*5}px;opacity:{round(0.4+(i%4)*0.15,2)};color:#B3E5FC;">❄</div>'
            for i in range(37)
        ])
        st.markdown(f"""
        <style>.stApp{{background:linear-gradient(180deg,#050a1a 0%,#0a1628 50%,#1a2a40 100%)!important;}}</style>
        <div id="wbg">{flakes}</div>
        <style>
        #wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;}}
        .sf{{position:absolute;top:-30px;animation:sfall linear infinite;text-shadow:0 0 10px rgba(179,229,252,0.9);}}
        @keyframes sfall{{0%{{top:-30px;transform:translateX(0) rotate(0deg);}}33%{{transform:translateX(20px) rotate(120deg);}}66%{{transform:translateX(-15px) rotate(240deg);}}100%{{top:110%;transform:translateX(10px) rotate(360deg);}}}}
        </style>""", unsafe_allow_html=True)

    # ─── 🌫️ FOG / MIST / HAZE ────────────────────────────────────────────────
    elif any(w in desc for w in ["fog", "mist", "haze", "smoke", "dust"]):
        st.markdown("""
        <style>.stApp{background:linear-gradient(180deg,#b0bec5 0%,#cfd8dc 50%,#eceff1 100%)!important;}</style>
        <div id="wbg"><div class="fog f1"></div><div class="fog f2"></div><div class="fog f3"></div><div class="fog f4"></div></div>
        <style>
        #wbg{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;}
        .fog{position:absolute;width:220%;height:100px;left:-110%;background:linear-gradient(90deg,transparent 0%,rgba(255,255,255,0.3) 30%,rgba(255,255,255,0.45) 50%,rgba(255,255,255,0.3) 70%,transparent 100%);border-radius:50%;animation:fdrift linear infinite;}
        .f1{top:15%;animation-duration:22s;}.f2{top:35%;animation-duration:28s;animation-delay:-10s;opacity:0.8;}.f3{top:55%;animation-duration:18s;animation-delay:-5s;opacity:0.6;}.f4{top:75%;animation-duration:32s;animation-delay:-15s;opacity:0.5;}
        @keyframes fdrift{0%{transform:translateX(-20%);}100%{transform:translateX(20%);}}
        </style>""", unsafe_allow_html=True)

    # ─── ☁️ CLOUDY — Sky Blue + Moving Clouds ─────────────────────────────────
    else:
        clouds = "".join([
            f'<div class="cc" style="top:{6+i*12}%;width:{220+i*55}px;height:{65+i*14}px;'
            f'animation-duration:{24+i*8}s;animation-delay:-{i*6}s;opacity:{0.88+i*0.02};"></div>'
            for i in range(5)
        ])
        st.markdown(f"""
        <style>.stApp{{background:linear-gradient(180deg,#5BA3D9 0%,#74B9E8 25%,#A8D5F0 55%,#D0EAFB 80%,#EAF6FF 100%)!important;}}</style>
        <div id="wbg">{clouds}</div>
        <style>
        #wbg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;}}
        .cc{{position:absolute;left:-300px;background:rgba(255,255,255,0.88);border-radius:80px;box-shadow:0 6px 24px rgba(80,140,200,0.12),inset 0 -4px 10px rgba(180,220,255,0.18);animation:ccmove linear infinite;}}
        .cc::before{{content:'';position:absolute;top:-48%;left:16%;width:50%;height:135%;background:rgba(255,255,255,0.92);border-radius:50%;}}
        .cc::after{{content:'';position:absolute;top:-36%;left:50%;width:38%;height:112%;background:rgba(245,252,255,0.88);border-radius:50%;}}
        @keyframes ccmove{{0%{{left:-300px;}}100%{{left:110%;}}}}
        </style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title"> ClimateIQ </div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-Powered Weather Intelligence · Real-Time Analytics · LSTM Forecasting</div>', unsafe_allow_html=True)
st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CITY INPUT
# ══════════════════════════════════════════════════════════════════════════════
col_inp, col_btn = st.columns([4, 1])
with col_inp:
    city = st.text_input("🏙️ Enter City Name", "Rajkot", placeholder="e.g. Mumbai, Delhi, London")
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    search = st.button("🔍 Analyze", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN LOGIC
# ══════════════════════════════════════════════════════════════════════════════
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

    # ✅ SET BACKGROUND
    set_weather_background(description, temp)

    aqi_val, aqi_label, aqi_emoji = get_aqi(lat, lon)

    # ── METRIC CARDS ───────────────────────────────────────────────────────────
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
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── STATUS + AQI + PRESSURE ────────────────────────────────────────────────
    col_desc, col_aqi, col_pres = st.columns(3)
    with col_desc:
        badge = "🔥 Hot Climate" if temp > 35 else ("❄️ Cold Climate" if temp < 10 else "🌤️ Comfortable")
        st.markdown(
            f'<div class="glass-card">'
            f'<div style="font-size:1.3rem;font-weight:700;color:#002a5c;">{badge}</div>'
            f'<div style="color:#004a8f;font-size:0.85rem;margin-top:4px;">{description}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col_aqi:
        aqi_colors = {1:"#00897B",2:"#7CB342",3:"#F9A825",4:"#E64A19",5:"#6A1B9A"}
        ac = aqi_colors.get(aqi_val, "#555")
        st.markdown(
            f'<div class="glass-card">'
            f'<div style="font-size:0.8rem;color:#004a8f;margin-bottom:6px;font-weight:600;">AIR QUALITY INDEX</div>'
            f'<span class="aqi-pill" style="background:{ac}22;color:{ac};border:1px solid {ac};">'
            f'{aqi_emoji} {aqi_label} (AQI {aqi_val})</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col_pres:
        st.markdown(
            f'<div class="glass-card">'
            f'<div style="font-size:0.8rem;color:#004a8f;margin-bottom:4px;font-weight:600;">PRESSURE</div>'
            f'<div style="font-size:1.6rem;font-weight:700;color:#0055aa;">{pressure} hPa</div>'
            f'<div style="font-size:0.8rem;color:#004a8f;">{"🔻 Low" if pressure < 1010 else "🔺 Normal"}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── ALERTS ─────────────────────────────────────────────────────────────────
    alerts = generate_alerts(temp, humidity, wind, aqi_val)
    if alerts:
        st.markdown('<div class="section-head">⚠️ SMART ALERTS</div>', unsafe_allow_html=True)
        for alert_type, msg in alerts:
            st.markdown(f'<div class="alert-{alert_type}">{msg}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── MAP + FORECAST ─────────────────────────────────────────────────────────
    map_col, chart_col = st.columns([1, 1])
    with map_col:
        st.markdown('<div class="section-head">📍 LOCATION MAP</div>', unsafe_allow_html=True)
        m = folium.Map(location=[lat, lon], zoom_start=10, tiles="OpenStreetMap")
        folium.Marker(
            [lat, lon],
            popup=f"<b>{city}</b><br>{temp}°C · {description}",
            tooltip=city,
            icon=folium.Icon(color="blue", icon="cloud"),
        ).add_to(m)
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
                fill="tozeroy",
                fillcolor="rgba(0,119,204,0.10)",
                name="Temperature °C",
            ))
            fig.update_layout(
                plot_bgcolor="rgba(255,255,255,0.35)",
                paper_bgcolor="rgba(255,255,255,0.25)",
                font=dict(color="#003366", size=11),
                xaxis=dict(gridcolor="rgba(0,80,160,0.15)", tickangle=-30),
                yaxis=dict(gridcolor="rgba(0,80,160,0.15)", title="°C"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=350,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Could not load forecast data.")

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── LSTM AI PREDICTION ─────────────────────────────────────────────────────
    st.markdown('<div class="section-head">🧠 LSTM AI TEMPERATURE PREDICTION (Next 7 Days)</div>', unsafe_allow_html=True)
    with st.spinner("🤖 Training LSTM model..."):
        real_temps = [i["main"]["temp"] for i in forecast_data["list"]] if "list" in forecast_data else []
        model      = train_model(real_temps)
        future_preds = predict_next(model, real_temps if real_temps else [temp], steps=7)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=[f"Day {i+1}" for i in range(7)],
        y=future_preds,
        marker=dict(
            color=future_preds,
            colorscale="RdYlGn_r",
            showscale=True,
            colorbar=dict(title="°C", tickfont=dict(color="#003366")),
        ),
        text=[f"{v:.1f}°C" for v in future_preds],
        textposition="outside",
        textfont=dict(color="#002a5c", size=12),
    ))
    fig2.update_layout(
        plot_bgcolor="rgba(255,255,255,0.35)",
        paper_bgcolor="rgba(255,255,255,0.25)",
        font=dict(color="#003366"),
        yaxis=dict(gridcolor="rgba(0,80,160,0.15)", title="Predicted Temp (°C)"),
        xaxis=dict(gridcolor="rgba(0,80,160,0.15)"),
        margin=dict(t=20, b=10, l=10, r=10),
        height=320,
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("⚡ LSTM model trained on live forecast data · Predictions are indicative")

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── AI CHATBOT ─────────────────────────────────────────────────────────────
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

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;color:#004a8f;font-size:0.8rem;font-weight:500;">'
    'ClimateIQ By Viren Solanki · Built with Streamlit + OpenWeatherMap + Gemini AI + TensorFlow LSTM'
    '</div>',
    unsafe_allow_html=True
)
