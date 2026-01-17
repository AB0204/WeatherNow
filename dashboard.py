import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# --- 1. CONFIG & ANIMATED CSS ---
st.set_page_config(page_title="WeatherNow", page_icon="⛈️", layout="wide")

st.markdown("""
<style>
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    
    .animate-enter {
        animation: fadeIn 0.8s ease-out forwards;
    }
    
    .weather-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        text-align: center;
        transition: transform 0.3s;
        margin-bottom: 20px;
    }
    .weather-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.15);
    }
    
    .alert-box {
        background: rgba(255, 87, 87, 0.2);
        border-left: 5px solid #ff5757;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        animation: pulse 2s infinite;
    }
    
    .minute-cast {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.3);
    }

    h1, h2, h3, p, div, span { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- IMPORTS ---
try:
    from services.weather_service import get_rich_weather_data
except ImportError:
    st.error("❌ Core services missing.")
    st.stop()

if 'favorites' not in st.session_state: st.session_state.favorites = ["London", "New York"]
if 'selected_city' not in st.session_state: st.session_state.selected_city = "London"

# --- HELPER: MINUTECAST LOGIC ---
def get_minutecast_text(minutely_data):
    if not minutely_data: return "MinuteCast unavailable"
    
    # Check next 4 chunks (1 hour)
    has_rain = any(m['precip'] > 0 for m in minutely_data)
    
    if not has_rain:
        return "☀️ No precipitation expected for the next 60 min."
    
    # Find start time
    for m in minutely_data:
        if m['precip'] > 0:
            t_obj = datetime.fromisoformat(m['time'])
            return f"🌧️ Precipitation starting at {t_obj.strftime('%H:%M')}"
            
    return "Variable conditions"

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1163/1163661.png", width=80)
    st.title("WeatherNow")
    
    st.subheader("⭐ My Places")
    for f in st.session_state.favorites:
        if st.button(f"📍 {f}", key=f):
            st.session_state.selected_city = f

    st.markdown("---")
    cities = st.multiselect("Compare", ["New York", "London", "Tokyo", "Paris", "Berlin", "Dubai", "Singapore"], default=[])

# --- MAIN ---
c1, c2 = st.columns([3,1])
with c1:
    search = st.text_input("Search Location", value=st.session_state.selected_city)
with c2:
    if st.button("❤️ Save"):
        if search not in st.session_state.favorites:
            st.session_state.favorites.append(search)
            st.toast("Saved!")

if search:
    with st.spinner("Scanning atmosphere..."):
        data = get_rich_weather_data(search)
        
        if not data:
            st.error("Location not found.")
        else:
            curr = data['current']
            
            # --- ALERTS SECTION ---
            # MinuteCast
            mc_text = get_minutecast_text(data.get('minutely', []))
            st.markdown(f"<div class='minute-cast animate-enter'>{mc_text}</div>", unsafe_allow_html=True)
            
            # Severe Weather
            if curr['wind_speed'] > 40:
                st.markdown(f"<div class='alert-box'>⚠️ HIGH WIND WARNING: {curr['wind_speed']} km/h gusts detected.</div>", unsafe_allow_html=True)
            if curr['uv_index'] > 7:
                 st.markdown(f"<div class='alert-box'>☀️ HIGH UV ALERT: Protection required.</div>", unsafe_allow_html=True)

            # --- HEADER METRICS ---
            col_main, col_detail = st.columns([1, 1.5])
            
            with col_main:
                st.markdown(f"""
                <div class='weather-card animate-enter'>
                    <h2 style='margin:0'>{data['city']}</h2>
                    <h1 style='font-size:5rem; margin:0'>{round(curr['temp'])}°</h1>
                    <p style='opacity:0.8'>Feels like {round(curr['feels_like'])}°</p>
                    <p style='font-size:1.2rem; text-transform:uppercase; letter-spacing:2px'>{curr.get('is_day') and 'DAY' or 'NIGHT'}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col_detail:
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown(f"<div class='weather-card animate-enter'>💧 Humidity<br><h1>{curr['humidity']}%</h1></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='weather-card animate-enter'>🌪️ Wind<br><h1>{curr['wind_speed']}</h1><small>km/h</small></div>", unsafe_allow_html=True)
                with c_b:
                     st.markdown(f"<div class='weather-card animate-enter'>☀️ UV Index<br><h1>{curr['uv_index']}</h1></div>", unsafe_allow_html=True)
                     st.markdown(f"<div class='weather-card animate-enter'>🍃 Air Quality<br><h1>{curr['aqi']}</h1></div>", unsafe_allow_html=True)

            # --- TABS ---
            t1, t2, t3 = st.tabs(["🌩️ Radar & Map", "📅 48h Forecast", "🌅 Astro & Details"])
            
            with t1:
                st.subheader("Live Precipitation Radar")
                # Folium with RainViewer
                m = folium.Map(location=[data['lat'], data['lon']], zoom_start=8, tiles='CartoDB dark_matter')
                
                # RainViewer Layer
                folium.TileLayer(
                    tiles="https://tile.rainviewer.com/v2/radar/nowcast_loop/512/{z}/{x}/{y}/2/1_1.png",
                    attr="RainViewer",
                    overlay=True,
                    name="Precipitation",
                    opacity=0.7
                ).add_to(m)
                
                folium.Marker([data['lat'], data['lon']], popup=data['city'], icon=folium.Icon(color="red", icon="cloud")).add_to(m)
                st_folium(m, width=900, height=500)
                st.caption("Radar data provided by RainViewer | Map by OpenStreetMap")

            with t2:
                st.subheader("hourly Forecast (48 Hours)")
                hourly_df = pd.DataFrame(data['hourly'])
                hourly_df['time'] = pd.to_datetime(hourly_df['time'])
                
                # Plotly Area Chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hourly_df['time'], y=hourly_df['temp'],
                    mode='lines', name='Temp',
                    line=dict(color='#00d2ff', width=3),
                    fill='tozeroy'
                ))
                fig.add_trace(go.Bar(
                    x=hourly_df['time'], y=hourly_df['prob'],
                    name='Rain %',
                    marker_color='rgba(255, 255, 255, 0.3)',
                    yaxis='y2'
                ))
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    yaxis=dict(title="Temp °C", showgrid=False),
                    yaxis2=dict(title="Rain %", overlaying='y', side='right', showgrid=False, range=[0, 100]),
                    hovermode="x unified",
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)

            with t3:
                # Astro Data (Sunrise/Sunset)
                today = data['daily'][0]
                sunrise = datetime.fromisoformat(today['sunrise']).strftime("%H:%M")
                sunset = datetime.fromisoformat(today['sunset']).strftime("%H:%M")
                
                c_sun, c_moon = st.columns(2)
                with c_sun:
                    st.markdown(f"""
                    <div class='weather-card'>
                        <h3>🌅 Sunrise</h3>
                        <h1>{sunrise}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                with c_moon:
                    st.markdown(f"""
                    <div class='weather-card'>
                        <h3>🌇 Sunset</h3>
                        <h1>{sunset}</h1>
                    </div>
                    """, unsafe_allow_html=True)
