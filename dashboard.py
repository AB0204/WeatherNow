import streamlit as st

# --- Config (Must be first) ---
st.set_page_config(
    page_title="WeatherNow",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import time
import requests
from datetime import datetime

# --- CSS (Glassmorphism) ---
st.markdown("""
<style>
    /* Background */
    .stApp {
        background: #0f2027;
        background: -webkit-linear-gradient(to right, #2c5364, #203a43, #0f2027);
        background: linear-gradient(to right, #2c5364, #203a43, #0f2027);
    }
    h1, h2, h3, h4, p, span, div { color: white !important; }
    
    /* Cards */
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        backdrop-filter: blur(5px);
    }
    .metric-val { font-size: 2.2rem; font-weight: bold; margin: 5px 0; }
    .metric-lbl { text-transform: uppercase; font-size: 0.9rem; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# --- Imports ---
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
    if "cloud" in d: return "☁️"
    if "rain" in d: return "🌧️"
    if "storm" in d: return "⛈️"
    if "snow" in d: return "❄️"
    return "🌈"

# --- Sidebar ---
with st.sidebar:
    st.title("🌤️ WeatherNow")
    cities = ["London", "New York", "Tokyo", "Paris", "Dubai", "Sydney", "Custom..."]
    sel = st.selectbox("Select City", cities)
    city = st.text_input("City Name", "San Francisco") if sel == "Custom..." else sel
    st.caption("Cloud Edition • v5.0 Lite")

# --- Main ---
st.title(f"{city}")
st.markdown(f"**{datetime.now().strftime('%A, %d %B')}**")

@st.cache_data(ttl=300)
def fetch(c): return get_weather_from_wttr(c)

tab1, tab2 = st.tabs(["🔥 Live", "📈 Trends"])

with tab1:
    if st.button("Refresh", type="primary"):
        try:
            raw = fetch(city)
            if raw:
                # Save
                db = next(get_db())
                save_weather_data(db, city, raw)
                
                # Parse
                cur = raw['current_condition'][0]
                desc = cur['weatherDesc'][0]['value']
                
                # Render
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"<div class='metric-card'><div class='metric-lbl'>Temp</div><div class='metric-val'>{cur['temp_C']}°</div></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='metric-card'><div class='metric-lbl'>Sky</div><div class='metric-val'>{get_emoji(desc)}</div></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='metric-card'><div class='metric-lbl'>Humid</div><div class='metric-val'>{cur['humidity']}%</div></div>", unsafe_allow_html=True)
                c4.markdown(f"<div class='metric-card'><div class='metric-lbl'>Wind</div><div class='metric-val'>{cur['windspeedKmph']}</div></div>", unsafe_allow_html=True)
                
                st.success("Updated")
            else:
                st.error("No data")
        except Exception as e:
            st.error(str(e))

with tab2:
    if st.button("Load History"):
        db = next(get_db())
        recs = get_history_stats(db, city, 30)
        if recs:
            df = pd.DataFrame([{"Date": r.timestamp, "Temp": r.temp_c} for r in recs])
            st.line_chart(df.set_index("Date")) # Native Chart (Fast)
        else:
            st.info("No history yet.")

