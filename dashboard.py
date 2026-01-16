import streamlit as st

# --- Config (Top Level) ---
st.set_page_config(
    page_title="WeatherNow",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import plotly.graph_objects as go
import time
import requests
from datetime import datetime
import traceback

# --- CSS (Glassmorphism) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: #0f2027;
        background: -webkit-linear-gradient(to right, #2c5364, #203a43, #0f2027);
        background: linear-gradient(to right, #2c5364, #203a43, #0f2027);
    }
    
    /* Headings & Text */
    h1, h2, h3, h4, p, span, div { color: #ffffff !important; }
    
    /* Metrics */
    .metric-container {
        border: 1px solid rgba(255,255,255,0.2);
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
        margin: 5px;
    }
    .metric-value { font-size: 2.5rem; font-weight: bold; margin: 10px 0; }
    .metric-label { font-size: 1rem; text-transform: uppercase; opacity: 0.8; }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white; border: none; padding: 10px 20px; border-radius: 8px;
        font-weight: bold; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- Imports (Safe) ---
try:
    from database import get_db, engine, Base
    from services.weather_service import get_weather_from_wttr, save_weather_data, get_history_stats
    Base.metadata.create_all(bind=engine)
except Exception as e:
    st.error(f"Startup Error: {e}")
    st.stop()

# --- Helpers ---
def get_emoji(desc):
    d = desc.lower()
    if "sun" in d or "clear" in d: return "☀️"
    if "partly" in d: return "⛅"
    if "cloud" in d: return "☁️"
    if "rain" in d or "drizzle" in d: return "🌧️"
    if "storm" in d or "thunder" in d: return "⛈️"
    if "snow" in d: return "❄️"
    if "mist" in d or "fog" in d: return "🌫️"
    return "🌈"

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4052/4052984.png", width=100) # Static Image instead of Lottie
    st.markdown("## 🌍 Location")
    cities = ["London", "New York", "Tokyo", "Paris", "Singapore", "Dubai", "Mumbai", "Sydney", "Berlin", "Toronto", "Custom..."]
    sel = st.selectbox("Select City", cities)
    city = st.text_input("City Name", "San Francisco") if sel == "Custom..." else sel
    st.markdown("---")
    st.caption(f"📍 Watching: {city}")

# --- Main ---
st.title(f"WeatherNow: {city}")
st.caption(f"Live Weather Intelligence • {datetime.now().strftime('%A, %d %B')}")

# Caching
@st.cache_data(ttl=300)
def get_data(city_name):
    return get_weather_from_wttr(city_name)

tab1, tab2, tab3 = st.tabs(["🔥 Live Status", "📉 Trends", "🔮 Forecast"])

with tab1:
    if st.button("Refresh Data", type="primary"):
        with st.spinner("Fetching..."):
            try:
                data_raw = get_data(city)
                if data_raw:
                    # Save
                    db = next(get_db())
                    save_weather_data(db, city, data_raw)
                    
                    # Parse
                    curr = data_raw['current_condition'][0]
                    desc = curr['weatherDesc'][0]['value']
                    emoji = get_emoji(desc)
                    
                    # Display
                    c1, c2, c3, c4 = st.columns(4)
                    
                    # Manual HTML Cards
                    c1.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-label">Temp</div>
                        <div class="metric-value">{curr['temp_C']}°</div>
                        <div>{curr['temp_F']}°F</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c2.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-label">Condition</div>
                        <div class="metric-value">{emoji}</div>
                        <div>{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c3.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-label">Humidity</div>
                        <div class="metric-value">{curr['humidity']}%</div>
                        <div>Relative</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c4.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-label">Wind</div>
                        <div class="metric-value">{curr['windspeedKmph']}</div>
                        <div>km/h</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.error("Server Busy.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("Click Refresh for Live Data")

with tab2:
    if st.button("Load History"):
        db = next(get_db())
        recs = get_history_stats(db, city, 30)
        if recs:
            df = pd.DataFrame([{"Date": r.timestamp, "Temp": r.temp_c} for r in recs])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Temp'], mode='lines+markers', line=dict(color='#00d2ff', width=3), fill='tozeroy'))
            fig.update_layout(title="Temperature Trend", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No history found.")

with tab3:
    st.info("ML Prediction Disabled (Cloud Safe Mode)")
    st.metric("Status", "Operational")

st.markdown("---")
st.caption("WeatherNow Reliable Edition")
