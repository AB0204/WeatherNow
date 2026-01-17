import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# --- 1. CONFIG & THEME ENGINE ---
st.set_page_config(page_title="WeatherNow", page_icon="🌤️", layout="wide")

# Dynamic Theme Logic
def get_theme(code, is_day):
    if is_day == 0: 
        return "linear-gradient(to bottom right, #0F2027, #203A43, #2C5364)", "#4ca1af" # Night
    if code in [0, 1]: 
        return "linear-gradient(to bottom right, #2980B9, #6DD5FA, #FFFFFF)", "#ffaa00" # Clear Day
    if code in [2, 3]: 
        return "linear-gradient(to bottom right, #4B79A1, #283E51)", "#add8e6" # Cloudy
    if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: 
        return "linear-gradient(to bottom right, #373B44, #4286f4)", "#00d2ff" # Rain
    if code in [71, 73, 75]: 
        return "linear-gradient(to bottom right, #83a4d4, #b6fbff)", "#ffffff" # Snow
    if code in [95, 96, 99]: 
        return "linear-gradient(to bottom right, #232526, #414345)", "#ff5555" # Storm
    return "linear-gradient(to bottom right, #1e3c72, #2a5298)", "#ffffff" # Default

# Safe Import
try:
    from services.weather_service import get_rich_weather_data
except ImportError:
    st.error("Service Error. Please check deployment.")
    st.stop()

# Initialize Session
if 'selected_city' not in st.session_state: st.session_state.selected_city = "New Delhi"
if 'favorites' not in st.session_state: st.session_state.favorites = ["New Delhi", "New York", "London"]

# Helper for MinuteCast
def get_minutecast_text(minutely_data):
    if not minutely_data: return "MinuteCast unavailable"
    has_rain = any(m['precip'] > 0 for m in minutely_data)
    if not has_rain: return "☀️ No rain expected in the next hour"
    for m in minutely_data:
        if m['precip'] > 0:
            return f"🌧️ Rain expected at {datetime.fromisoformat(m['time']).strftime('%H:%M')}"
    return "Variable conditions"

# Fetch Data FIRST to determine Theme
with st.spinner("Connecting to satellites..."):
    data = get_rich_weather_data(st.session_state.selected_city)

bg_gradient = "linear-gradient(to right, #2c3e50, #4ca1af)"
if data:
    bg_gradient, accent_color = get_theme(data['current']['weather_code'], data['current']['is_day'])

# --- 2. CSS MASTERPIECE ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}
    
    .stApp {{
        background: {bg_gradient};
        color: white;
    }}
    
    .hero-container {{
        text-align: center;
        padding: 40px 20px;
        animation: fadeIn 1s ease-in;
    }}
    
    .hero-temp {{
        font-size: 8rem;
        font-weight: 800;
        line-height: 1;
        text-shadow: 0 4px 10px rgba(0,0,0,0.3);
        margin: 0;
    }}
    
    .glass-card {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
        margin-bottom: 15px;
        height: 100%;
        text-align: center;
    }}
    
    .glass-card:hover {{
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.15);
    }}
    
    .minutecast-pill {{
        background: rgba(0, 0, 0, 0.3);
        border-radius: 50px;
        padding: 10px 30px;
        display: inline-block;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 30px;
        font-weight: 600;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    h1, h2, h3, p, div, span, label {{ color: white !important; }}
    
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1163/1163661.png", width=60)
    st.markdown("### WeatherNow")
    
    # Locate Me
    if st.button("📍 Locate Me", use_container_width=True):
        try:
            loc_res = requests.get('https://ipinfo.io/json', timeout=2).json()
            if 'city' in loc_res:
                st.session_state.selected_city = loc_res['city']
                st.rerun()
            else:
                st.warning("Could not locate IP.")
        except:
            st.warning("Location service unavailable.")

    # Search
    new_city = st.text_input("🔍 Search City", value="")
    if new_city: st.session_state.selected_city = new_city
    
    st.markdown("---")
    
    # Favorites
    st.caption("SAVED")
    for fav in st.session_state.favorites:
        if st.button(f"❤️ {fav}", key=f"fav_{fav}", use_container_width=True):
            st.session_state.selected_city = fav
            
    st.markdown("---")
    
    # MASSIVE CITY LIST
    st.caption("INDIA")
    india_cities = ["New Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Chandigarh", "Goa", "Kochi"]
    st.selectbox("Select Indian City", india_cities, index=None, key="india_sel", on_change=lambda: st.session_state.update(selected_city=st.session_state.india_sel) if st.session_state.india_sel else None)
    
    st.caption("USA")
    usa_cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Seattle", "Denver", "Boston", "Las Vegas", "Miami", "San Francisco"]
    st.selectbox("Select US City", usa_cities, index=None, key="usa_sel", on_change=lambda: st.session_state.update(selected_city=st.session_state.usa_sel) if st.session_state.usa_sel else None)
    
    st.caption("EUROPE")
    eu_cities = ["London", "Paris", "Berlin", "Madrid", "Rome", "Amsterdam", "Vienna", "Lisbon", "Warsaw", "Prague", "Budapest", "Stockholm", "Oslo", "Copenhagen", "Zurich", "Athens", "Dublin", "Brussels", "Helsinki"]
    st.selectbox("Select EU City", eu_cities, index=None, key="eu_sel", on_change=lambda: st.session_state.update(selected_city=st.session_state.eu_sel) if st.session_state.eu_sel else None)
    
    st.caption("GLOBAL")
    global_cities = ["Tokyo", "Dubai", "Singapore", "Sydney", "Beijing", "Seoul", "Bangkok", "Istanbul", "São Paulo", "Toronto", "Moscow", "Cairo", "Cape Town", "Rio de Janeiro"]
    st.selectbox("Select Global City", global_cities, index=None, key="global_sel", on_change=lambda: st.session_state.update(selected_city=st.session_state.global_sel) if st.session_state.global_sel else None)

# --- 4. MAIN CONTENT ---
if not data:
    st.error("Wait... retrying connection.")
    st.stop()

curr = data['current']

# A. HERO SECTION
st.markdown(f"""
<div class="hero-container">
    <div style="font-size: 2.5rem; opacity: 0.9;">{data['city']}</div>
    <div style="font-size: 1.2rem; opacity: 0.6;">{data['country']}</div>
    <div class="hero-temp">{round(curr['temp'])}°</div>
    <div style="font-size: 1.5rem; opacity: 0.8; text-transform:uppercase; margin-bottom: 20px;">{get_minutecast_text(data.get('minutely'))}</div>
    <div class="minutecast-pill">Feels like {round(curr['feels_like'])}° • High UV: {curr['uv_index']} • Wind: {curr['wind_speed']} km/h</div>
</div>
""", unsafe_allow_html=True)

# B. MAIN METRICS GRID
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="glass-card">
        <div style="text-transform:uppercase; font-size:0.8rem; opacity:0.7">Humidity</div>
        <div style="font-size:2rem; font-weight:600">{curr['humidity']}%</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="glass-card">
        <div style="text-transform:uppercase; font-size:0.8rem; opacity:0.7">Air Quality</div>
        <div style="font-size:2rem; font-weight:600">{curr['aqi']}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="glass-card">
        <div style="text-transform:uppercase; font-size:0.8rem; opacity:0.7">Sunrise</div>
        <div style="font-size:2rem; font-weight:600">{datetime.fromisoformat(data['daily'][0]['sunrise']).strftime('%H:%M')}</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="glass-card">
        <div style="text-transform:uppercase; font-size:0.8rem; opacity:0.7">Sunset</div>
        <div style="font-size:2rem; font-weight:600">{datetime.fromisoformat(data['daily'][0]['sunset']).strftime('%H:%M')}</div>
    </div>""", unsafe_allow_html=True)

# C. TABS (Forecast / Radar)
st.markdown("###")
t1, t2 = st.tabs(["📅 48-Hour Forecast", "🗺️ Weather Radar"])

with t1:
    hourly_df = pd.DataFrame(data['hourly'])
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hourly_df['time'], y=hourly_df['temp'],
        fill='tozeroy', mode='lines',
        line=dict(width=4, color='white'),
        fillcolor='rgba(255, 255, 255, 0.1)',
        name='Temp'
    ))
    
    fig.add_trace(go.Bar(
        x=hourly_df['time'], y=hourly_df['prob'],
        yaxis='y2', name='Rain %',
        marker_color='rgba(255, 255, 255, 0.3)'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family='Poppins'),
        yaxis=dict(showgrid=False, showticklabels=False),
        yaxis2=dict(overlaying='y', side='right', range=[0, 100], showgrid=False, showticklabels=False),
        margin=dict(l=0, r=0, t=20, b=0),
        height=300,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### 7-Day Outlook")
    cols = st.columns(7)
    for i, day in enumerate(data['daily'][:7]):
        d_name = datetime.fromisoformat(day['date']).strftime("%a")
        with cols[i]:
            st.markdown(f"""
            <div class="glass-card" style="padding: 10px; font-size: 0.8rem;">
                <div style="opacity:0.7">{d_name}</div>
                <div style="font-weight:bold; font-size:1.1rem; margin: 5px 0;">{round(day['max_temp'])}°</div>
                <div style="opacity:0.7">{round(day['min_temp'])}°</div>
            </div>
            """, unsafe_allow_html=True)

with t2:
    m = folium.Map(location=[data['lat'], data['lon']], zoom_start=9, tiles='CartoDB dark_matter')
    folium.TileLayer(
        tiles="https://tile.rainviewer.com/v2/radar/nowcast_loop/512/{z}/{x}/{y}/2/1_1.png",
        attr="RainViewer", overlay=True, name="Rain", opacity=0.7
    ).add_to(m)
    st_folium(m, width=1200, height=450)

st.markdown("<div style='text-align:center; padding: 20px; opacity: 0.5; font-size: 0.8rem'>WeatherNow Ultimate v10 • Antigravity</div>", unsafe_allow_html=True)
