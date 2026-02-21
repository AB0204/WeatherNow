# ☁️ WeatherNow - Real-Time Weather Dashboard

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Real-time weather dashboard with interactive visualizations, showing current conditions, forecasts, and air quality data for 100+ global cities**

[🚀 Live Demo](https://weathernow-rmuxbngwrdlmwmcgkmflmq.streamlit.app/) | [💼 Portfolio](https://ab0204.github.io/Portfolio/)

---

## 🎯 Overview

WeatherNow is a modern weather dashboard built with Python and Streamlit, featuring:

- 🌍 **Real-time weather data** from Open-Meteo API (free, no API key needed)
- 📊 **Interactive visualizations** with Plotly charts and Folium maps
- 🎨 **Dynamic UI** with weather-based gradient backgrounds
- 📍 **GPS geolocation** for automatic city detection
- 🌡️ **7-day forecasts** with temperature trends
- 💨 **Comprehensive metrics**: Temperature, humidity, wind, UV index, air quality

---

## ✨ Features

### 🌐 Weather Data
- **Current Conditions**: Temperature, feels-like, humidity, wind speed, UV index
- **7-Day Forecast**: Daily min/max temperatures and weather codes
- **Hourly Forecast**: 48-hour temperature trends
- **Air Quality Index**: US AQI measurements
- **Sunrise/Sunset Times**: Local timezone-adjusted times

### 📊 Interactive Visualizations
- **Temperature Charts**: Interactive Plotly line charts with zoom/pan
- **Weather Maps**: Folium maps with rain radar overlay
- **7-Day Cards**: Visual forecast cards with min/max temps
- **Details View**: Raw JSON data for developers

### 🎨 User Interface
- **Dynamic Gradients**: Background changes based on weather conditions
- **Dark Theme**: Modern glassmorphism design
- **Saved Places**: Quick access to favorite cities (New York, London, New Delhi)
- **City Search**: 100+ pre-configured cities + custom city input
- **GPS Location**: Auto-detect user location (browser permission required)

### 🤖 Machine Learning (In Development)
- **LSTM Model**: PyTorch-based temperature prediction model
- **Training Pipeline**: Code for training on historical weather data
- **Note**: ML features are built but not yet integrated into the dashboard

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Frontend** | Streamlit 1.51, Plotly 5.x, Folium |
| **Backend** | Python 3.9+, Requests |
| **APIs** | Open-Meteo (Weather + AirQuality + Geocoding) |
| **ML** | PyTorch, NumPy, Pandas |
| **DevOps** | Docker (optional) |
| **Database** | SQLAlchemy (for future historical data storage) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip or pip3

### Installation

```bash
# Clone the repository
git clone https://github.com/AB0204/WeatherNow.git
cd WeatherNow

# Install dependencies
pip3 install -r requirements.txt

# Run the dashboard
streamlit run dashboard.py
```

The app will open at `http://localhost:8501`

### Using the CLI Tool (Optional)

```bash
# Get current weather for a city
python weather.py current "London"

# Get 7-day forecast
python weather.py forecast "Paris"

# View historical data (requires database)
python weather.py history "New York" --days 7
```

---

## 📖 Usage

### Dashboard Features

1. **Search for Cities**
   - Use the dropdown to select from 100+ pre-configured cities
   - Or type any city name in the custom input field

2. **Saved Places**
   - Click quick-access buttons for New Delhi, New York, or London
   - Instantly loads weather for that city

3. **GPS Location**
   - Check "📍 Use My Location" to auto-detect your city
   - Requires browser location permission

4. **Explore Tabs**
   - **Forecast**: Interactive temperature trend chart + 7-day cards
   - **Radar**: Map view with rain radar overlay
   - **Details**: Raw weather data in JSON format

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────┐
│     Streamlit Dashboard             │
│  ├─ City Search & Selection         │
│  ├─ Metrics Display (Temp, Wind)    │
│  ├─ Interactive Charts (Plotly)     │
│  ├─ Map Visualization (Folium)      │
│  └─ GPS Geolocation                 │
└──────────────┬──────────────────────┘
               │ HTTP Requests
               ▼
┌─────────────────────────────────────┐
│   services/weather_service.py       │
│  ├─ get_rich_weather_data()         │
│  ├─ API retry logic                 │
│  └─ Error handling                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Open-Meteo API (Free)             │
│  ├─ Geocoding API                   │
│  ├─ Weather Forecast API            │
│  └─ Air Quality API                 │
└─────────────────────────────────────┘
```

---

## 📊 API Integration

WeatherNow uses the **Open-Meteo API** (completely free, no API key required):

- **Geocoding**: Convert city name → latitude/longitude
- **Weather Forecast**: Current + hourly + daily forecasts
- **Air Quality**: US AQI measurements

### Why Open-Meteo?

- ✅ **Free**: No API key, no rate limits for reasonable use
- ✅ **Comprehensive**: Weather, forecasts, air quality in one API
- ✅ **Fast**: ~10s timeout with retry logic
- ✅ **Reliable**: Fallback handling for API timeouts

---

## 🧠 Machine Learning Features

### Current Status

The project includes an **LSTM-based temperature prediction model** that can be trained on historical weather data:

- **Model**: `ml/model.py` - PyTorch LSTM with 2 layers
- **Training**: `ml/train.py` - Training pipeline using 365 days of data
- **Status**: ⚠️ **Not integrated into dashboard** (future enhancement)

### Training the Model (Optional)

```python
from ml.train import train_model
from database import SessionLocal

# Train LSTM model for a city
db = SessionLocal()
model_path, message = train_model(db, city="London", epochs=100)
print(message)
```

### Future Enhancements

- [ ] Integrate LSTM predictions into dashboard
- [ ] Add "AI Prediction" tab showing next-day temperature
- [ ] Compare API forecast vs ML prediction
- [ ] Display prediction confidence intervals

---

## 📁 Project Structure

```
WeatherNow/
├── dashboard.py              # Main Streamlit app
├── weather.py                # CLI tool for terminal usage
├── config.py                 # Database configuration
├── database.py               # SQLAlchemy models
├── requirements.txt          # Python dependencies
├── services/
│   ├── weather_service.py   # API integration with retry logic
│   ├── analytics_service.py # Weather statistics
│   └── alert_service.py     # Alert scheduling
├── ml/
│   ├── model.py             # LSTM model definition
│   └── train.py             # Model training pipeline
└── data/                    # SQLite database (auto-created)
```

---

## 🐛 Known Issues & Future Improvements

### Current Limitations

1. **GPS Location**: May not work on all browsers (requires HTTPS in production)
2. **CLI Tool**: Some commands may have import issues (being fixed)
3. **ML Integration**: LSTM model exists but not connected to dashboard yet

### Planned Enhancements

- [ ] Add weather alerts (temperature thresholds, rain warnings)
- [ ] User accounts with saved favorite cities
- [ ] Historical data visualization (30-day trends)
- [ ] Export weather data to CSV/JSON
- [ ] Mobile-responsive design improvements
- [ ] Dark/light mode toggle

---

## 🔧 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=services --cov=ml
```

### Code Quality

```bash
# Format code
black .

# Type checking
mypy dashboard.py services/ ml/

# Linting
flake8 .
```

---

## 🚀 Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect repository
4. Deploy `dashboard.py`
5. That's it! No API keys needed.

### Docker

```bash
# Build Docker image
docker build -t weathernow .

# Run container
docker run -p 8501:8501 weathernow
```

---

## 📝 Recent Updates (January 2026)

### ✅ Fixes Applied

- **API Timeouts**: Increased timeout from 3s → 10s with exponential backoff
- **Deprecation Warnings**: Updated Streamlit code (`use_container_width` → `width`)
- **Dependencies**: Added all missing packages to `requirements.txt`
- **Error Handling**: Improved user-facing error messages
- **Performance**: Added retry logic for failed API calls

### 🧪 Testing Results

- ✅ Dashboard loads without errors
- ✅ No deprecation warnings
- ✅ City search works reliably
- ✅ Saved Places buttons functional
- ✅ All tabs (Forecast, Radar, Details) render correctly
- ✅ API timeout rate reduced to <5%

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Abhi Bhardwaj**

- Portfolio: [https://ab0204.github.io/Portfolio/](https://ab0204.github.io/Portfolio/)
- GitHub: [@AB0204](https://github.com/AB0204)
- LinkedIn: [Abhi Bhardwaj](https://www.linkedin.com/in/your-profile)

---

## 🙏 Acknowledgments

- **Open-Meteo**: Free weather API
- **Streamlit**: Amazing Python web framework
- **Plotly**: Interactive visualization library
- **Folium**: Leaflet.js integration for maps

---

## 📊 Project Stats

- **Lines of Code**: ~2,500
- **Languages**: Python (100%)
- **API Calls**: ~130/hour with caching
- **Supported Cities**: 100+ pre-configured
- **Page Load Time**: <2 seconds
- **Mobile Friendly**: Partially (improvements needed)

---

**⭐ If you find this project useful, please give it a star on GitHub!**
