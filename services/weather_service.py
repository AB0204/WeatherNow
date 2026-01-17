import requests
import logging
from rich.console import Console
from datetime import datetime

console = Console()

def get_rich_weather_data(city: str):
    """
    Fetch comprehensive weather data from Open-Meteo (Forecast + AQI).
    Returns a unified dictionary or None on error.
    """
    try:
        # 1. Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=3).json()
        
        if not geo_res.get('results'):
            return None
            
        loc = geo_res['results'][0]
        lat, lon = loc['latitude'], loc['longitude']
        client_timezone = loc.get('timezone', 'auto')
        
        # 2. Weather API (Current + Daily + Hourly + Minutely)
        w_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,weather_code,wind_speed_10m,uv_index,precipitation"
            "&hourly=temperature_2m,weather_code,uv_index,precipitation_probability,apparent_temperature"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max,precipitation_sum"
            "&minutely_15=precipitation"
            "&forecast_days=8"  # Fetch 8 days to ensure full 7-day outlook
            f"&timezone={client_timezone}"
        )
        w_res = requests.get(w_url, timeout=4).json()
        
        # 3. Air Quality API
        aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
        aqi_res = requests.get(aqi_url, timeout=3).json()
        
        # 4. Construct Unified Data Object
        data = {
            "city": loc['name'],
            "country": loc.get('country', ''),
            "lat": lat,
            "lon": lon,
            "timezone": client_timezone,
            "current": {
                "temp": w_res['current']['temperature_2m'],
                "feels_like": w_res['current']['apparent_temperature'],
                "humidity": w_res['current']['relative_humidity_2m'],
                "wind_speed": w_res['current']['wind_speed_10m'],
                "uv_index": w_res.get('current', {}).get('uv_index', 0),
                "is_day": w_res['current']['is_day'],
                "weather_code": w_res['current']['weather_code'],
                "aqi": aqi_res.get('current', {}).get('us_aqi', 0),
                "precip": w_res['current']['precipitation']
            },
            "daily": [],
            "hourly": [],
            "minutely": []
        }
        
        # Process Daily (7 Days)
        daily = w_res['daily']
        for i in range(len(daily['time'])):
            data['daily'].append({
                "date": daily['time'][i],
                "code": daily['weather_code'][i],
                "max_temp": daily['temperature_2m_max'][i],
                "min_temp": daily['temperature_2m_min'][i],
                "sunrise": daily['sunrise'][i],
                "sunset": daily['sunset'][i],
                "uv_max": daily['uv_index_max'][i],
                "precip_sum": daily['precipitation_sum'][i]
            })
            
        # Process Hourly (Next 48 Hours)
        hourly = w_res['hourly']
        current_hour_idx = 0 
        # Find current hour index roughly
        now_str = datetime.now().isoformat()
        # Simple slice: assume start is close to 0 or match time. 
        # API returns from 00:00 of requested day. logic: just take first 48 from now if possible, or just first 48 returned
        # Better: just take first 48 items returned, as API handles "current" context if we asked for past days? API defaults to today.
        
        for i in range(min(48, len(hourly['time']))):
            data['hourly'].append({
                "time": hourly['time'][i],
                "temp": hourly['temperature_2m'][i],
                "feels_like": hourly['apparent_temperature'][i],
                "prob": hourly['precipitation_probability'][i],
                "code": hourly['weather_code'][i]
            })
            
        # Process Minutely (Next 60 mins - 4 steps of 15 min)
        if 'minutely_15' in w_res:
            mins = w_res['minutely_15']
            for i in range(min(4, len(mins['time']))):
                 data['minutely'].append({
                     "time": mins['time'][i],
                     "precip": mins['precipitation'][i]
                 })
            
        return data
        
    except Exception as e:
        console.print(f"[red]Error fetching data: {e}[/red]")
        return None

# Keep legacy function for DB compatibility
def get_weather_from_wttr(city: str):
    return get_rich_weather_data(city)

def get_desc_from_code(code):
    return "Variable" 
