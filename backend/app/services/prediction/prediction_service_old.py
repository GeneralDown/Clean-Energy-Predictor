"""
Prediction service for clean-energy forecasting platform.
Uses Open-Meteo forecast data + trained ML model (weather + time features only).
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple

import requests
import pandas as pd
import joblib
import xgboost as xgb
from fastapi import HTTPException

from app.models.prediction import PredictionPoint

logger = logging.getLogger(__name__)

# -------------------------
# Load trained ML model
# -------------------------
MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "ml" / "carbon_intensity_rank_xgb.pkl"
bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
features = bundle["features"]
MODEL_VERSION = "weather_time_v1"

# -------------------------
# API Config
# -------------------------
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_URL = "https://nominatim.openstreetmap.org/search"

# -------------------------
# Geocoding
# -------------------------
def geocode_location(location: str) -> Tuple[float, float]:
    """
    Convert a location name into (latitude, longitude) using Nominatim.
    """
    try:
        params = {
            "q": location,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "CleanEnergyForecast/1.0"  # Required by Nominatim
        }
        r = requests.get(GEOCODE_URL, params=params, headers=headers)
        r.raise_for_status()
        results = r.json()
        if not results:
            raise HTTPException(status_code=404, detail=f"Location '{location}' not found")
        lat = float(results[0]["lat"])
        lon = float(results[0]["lon"])
        return lat, lon
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Geocoding failed for '{location}': {e}")
        raise HTTPException(status_code=500, detail=f"Geocoding failed: {e}")

# -------------------------
# Weather forecast
# -------------------------
def get_weather_forecast(lat: float, lon: float, hours_ahead: int = 24) -> pd.DataFrame:
    """
    Fetch hourly weather forecast from Open-Meteo for the given coordinates.
    Returns a DataFrame with temperature_c, humidity_percent, cloud_cover_percent, wind_speed_mps.
    """
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,cloudcover,windspeed_10m",
            "forecast_days": min((hours_ahead // 24) + 1, 7),  # up to 7 days
            "timezone": "UTC"
        }
        r = requests.get(OPEN_METEO_URL, params=params)
        r.raise_for_status()
        data = r.json()

        # Convert wind speed from km/h to m/s
        wind_speeds_mps = [(w / 3.6) if w is not None else None for w in data["hourly"]["windspeed_10m"]]

        df = pd.DataFrame({
            "datetime": pd.to_datetime(data["hourly"]["time"], utc=True),
            "temperature_c": data["hourly"]["temperature_2m"],
            "humidity_percent": data["hourly"]["relative_humidity_2m"],
            "cloud_cover_percent": data["hourly"]["cloudcover"],
            "wind_speed_mps": wind_speeds_mps
        })

        # Limit to requested hours
        df = df.head(hours_ahead).reset_index(drop=True)
        return df

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Weather API HTTP error: {http_err}")
        raise HTTPException(status_code=400, detail=f"Weather API error: {http_err}")
    except Exception as e:
        logger.error(f"Weather API fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Weather API fetch failed: {e}")

# -------------------------
# Feature engineering
# -------------------------
def preprocess_input(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add time-based features to match training.
    """
    df["hour_of_day"] = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.dayofweek
    df["month"] = df["datetime"].dt.month
    return df

# -------------------------
# Main Prediction Function
# -------------------------
async def generate_predictions(location: str, hours_ahead: int = 24) -> dict:
    """
    Generate predictions for a given location name using weather forecast data + ML model.
    Works for any forecast horizon (no lag/rolling CI features).
    """
    try:
        # 1. Geocode location to lat/lon
        lat, lon = geocode_location(location)

        # 2. Fetch weather forecast
        weather_df = get_weather_forecast(lat, lon, hours_ahead)

        # 3. Add time features
        df_proc = preprocess_input(weather_df)

        # 4. Select only model features
        X = df_proc[features]

        # 5. Predict cleanliness ranking score
        dmat = xgb.DMatrix(X)
        df_proc["predicted_score"] = model.predict(dmat)

        # 6. Normalize to 0–100 cleanliness scale
        max_score = df_proc["predicted_score"].max()
        min_score = df_proc["predicted_score"].min()
        df_proc["cleanliness_score"] = ((df_proc["predicted_score"] - min_score) /
                                        (max_score - min_score) * 100).round(1)

        # 7. Build PredictionPoint list
        prediction_points = [
            PredictionPoint(
                timestamp=row["datetime"],
                cleanliness_score=row["cleanliness_score"],
                confidence=None,
                carbon_intensity=None  # Not predicted in this model
            )
            for _, row in df_proc.iterrows()
        ]

        # 8. Identify best hour
        best_point = max(prediction_points, key=lambda p: p.cleanliness_score)
        best_hour = {
            "timestamp": best_point.timestamp,
            "cleanliness_score": best_point.cleanliness_score,
            "confidence": best_point.confidence
        }

        # 9. Return combined result
        return {
            "location": location,
            "generated_at": datetime.utcnow(),
            "predictions": prediction_points,
            "best_clean_energy_hour": best_hour,
            "model_version": MODEL_VERSION,
            "data_freshness": "live"
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Prediction generation failed: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

"""
Prediction service for clean-energy forecasting platform.
Uses Open-Meteo forecast data + trained ML model (weather + time features only).
"""

import logging
from datetime import datetime, date
from pathlib import Path
from typing import Tuple, Optional

import requests
import pandas as pd
import joblib
import xgboost as xgb
from fastapi import HTTPException

from app.models.prediction import PredictionPoint

logger = logging.getLogger(__name__)

# -------------------------
# Load trained ML model
# -------------------------
MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "ml" / "carbon_intensity_rank_xgb.pkl"
bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
features = bundle["features"]
MODEL_VERSION = "weather_time_v1"

# -------------------------
# API Config
# -------------------------
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_URL = "https://nominatim.openstreetmap.org/search"

# -------------------------
# Geocoding
# -------------------------
def geocode_location(location: str) -> Tuple[float, float]:
    try:
        params = {"q": location, "format": "json", "limit": 1}
        headers = {"User-Agent": "CleanEnergyForecast/1.0"}
        r = requests.get(GEOCODE_URL, params=params, headers=headers)
        r.raise_for_status()
        results = r.json()
        if not results:
            raise HTTPException(status_code=404, detail=f"Location '{location}' not found")
        return float(results[0]["lat"]), float(results[0]["lon"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Geocoding failed for '{location}': {e}")
        raise HTTPException(status_code=500, detail=f"Geocoding failed: {e}")

# -------------------------
# Weather forecast
# -------------------------
def get_weather_forecast(lat: float, lon: float, hours_ahead: int = 168) -> pd.DataFrame:
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,cloudcover,windspeed_10m",
            "forecast_days": min((hours_ahead // 24) + 1, 7),
            "timezone": "UTC"
        }
        r = requests.get(OPEN_METEO_URL, params=params)
        r.raise_for_status()
        data = r.json()

        wind_speeds_mps = [(w / 3.6) if w is not None else None for w in data["hourly"]["windspeed_10m"]]

        df = pd.DataFrame({
            "datetime": pd.to_datetime(data["hourly"]["time"], utc=True),
            "temperature_c": data["hourly"]["temperature_2m"],
            "humidity_percent": data["hourly"]["relative_humidity_2m"],
            "cloud_cover_percent": data["hourly"]["cloudcover"],
            "wind_speed_mps": wind_speeds_mps
        })
        return df.reset_index(drop=True)
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Weather API HTTP error: {http_err}")
        raise HTTPException(status_code=400, detail=f"Weather API error: {http_err}")
    except Exception as e:
        logger.error(f"Weather API fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Weather API fetch failed: {e}")

# -------------------------
# Feature engineering
# -------------------------
def preprocess_input(df: pd.DataFrame) -> pd.DataFrame:
    df["hour_of_day"] = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.dayofweek
    df["month"] = df["datetime"].dt.month
    return df

# -------------------------
# Impact equivalents
# -------------------------
def calculate_impact(avg_score: float, best_score: float, duration_hours: int) -> dict:
    # Simple placeholder: assume each +10 cleanliness points saves 1kg CO2
    co2_saved_kg = max(0, (best_score - avg_score) / 10.0) * duration_hours
    trees_planted = round(co2_saved_kg / 21.77, 2)  # 1 tree ~ 21.77kg CO2/year
    km_car_avoided = round(co2_saved_kg / 0.192, 1)  # avg petrol car ~192g CO2/km
    return {
        "co2_saved_kg": round(co2_saved_kg, 2),
        "trees_planted_equiv": trees_planted,
        "km_car_avoided_equiv": km_car_avoided
    }

# -------------------------
# Main Prediction Function
# -------------------------
async def generate_predictions(
    location: str,
    hours_ahead: int = 24,
    day: Optional[str] = None,
    duration_hours: int = 1
) -> dict:
    try:
        lat, lon = geocode_location(location)
        weather_df = get_weather_forecast(lat, lon, hours_ahead=168)  # fetch full 7 days

        df_proc = preprocess_input(weather_df)
        X = df_proc[features]
        dmat = xgb.DMatrix(X)
        df_proc["predicted_score"] = model.predict(dmat)

        max_score = df_proc["predicted_score"].max()
        min_score = df_proc["predicted_score"].min()
        df_proc["cleanliness_score"] = ((df_proc["predicted_score"] - min_score) /
                                        (max_score - min_score) * 100).round(1)

        # Filter by day if provided
        if day:
            target_date = pd.to_datetime(day).date()
            df_proc = df_proc[df_proc["datetime"].dt.date == target_date]
            if df_proc.empty:
                raise HTTPException(status_code=404, detail=f"No forecast data for {day}")

        # Find best N-hour window
        scores = df_proc["cleanliness_score"].tolist()
        best_start_idx = 0
        best_avg = -1
        for i in range(len(scores) - duration_hours + 1):
            avg_window = sum(scores[i:i+duration_hours]) / duration_hours
            if avg_window > best_avg:
                best_avg = avg_window
                best_start_idx = i

        best_block = df_proc.iloc[best_start_idx:best_start_idx+duration_hours]
        impact = calculate_impact(avg_score=sum(scores)/len(scores),
                                  best_score=best_avg,
                                  duration_hours=duration_hours)

        prediction_points = [
            PredictionPoint(
                timestamp=row["datetime"],
                cleanliness_score=row["cleanliness_score"],
                confidence=None,
                carbon_intensity=None
            )
            for _, row in df_proc.iterrows()
        ]

        return {
            "location": location,
            "generated_at": datetime.utcnow(),
            "predictions": prediction_points,
            "recommended_window": {
                "start": best_block.iloc[0]["datetime"],
                "end": best_block.iloc[-1]["datetime"],
                "average_cleanliness_score": round(best_avg, 1),
                "impact": impact
            },
            "model_version": MODEL_VERSION,
            "data_freshness": "live"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))






"""
Prediction service for clean-energy forecasting platform.
Uses Open-Meteo forecast data + trained ML model (weather + time features only).
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

import requests
import pandas as pd
import joblib
import xgboost as xgb
from fastapi import HTTPException

from app.models.prediction import PredictionPoint

logger = logging.getLogger(__name__)

# -------------------------
# Load trained ML model
# -------------------------
MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "ml" / "carbon_intensity_rank_xgb.pkl"
bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
features = bundle["features"]
MODEL_VERSION = "weather_time_v1"

# -------------------------
# API Config
# -------------------------
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_URL = "https://nominatim.openstreetmap.org/search"

# -------------------------
# Geocoding
# -------------------------
def geocode_location(location: str) -> Tuple[float, float]:
    try:
        params = {"q": location, "format": "json", "limit": 1}
        headers = {"User-Agent": "CleanEnergyForecast/1.0"}
        r = requests.get(GEOCODE_URL, params=params, headers=headers)
        r.raise_for_status()
        results = r.json()
        if not results:
            raise HTTPException(status_code=404, detail=f"Location '{location}' not found")
        return float(results[0]["lat"]), float(results[0]["lon"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Geocoding failed for '{location}': {e}")
        raise HTTPException(status_code=500, detail=f"Geocoding failed: {e}")

# -------------------------
# Weather forecast
# -------------------------
def get_weather_forecast(lat: float, lon: float, hours_ahead: int = 168) -> pd.DataFrame:
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,cloudcover,windspeed_10m",
            "forecast_days": min((hours_ahead // 24) + 1, 7),
            "timezone": "UTC"
        }
        r = requests.get(OPEN_METEO_URL, params=params)
        r.raise_for_status()
        data = r.json()

        wind_speeds_mps = [(w / 3.6) if w is not None else None for w in data["hourly"]["windspeed_10m"]]

        df = pd.DataFrame({
            "datetime": pd.to_datetime(data["hourly"]["time"], utc=True),
            "temperature_c": data["hourly"]["temperature_2m"],
            "humidity_percent": data["hourly"]["relative_humidity_2m"],
            "cloud_cover_percent": data["hourly"]["cloudcover"],
            "wind_speed_mps": wind_speeds_mps
        })
        return df.reset_index(drop=True)
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Weather API HTTP error: {http_err}")
        raise HTTPException(status_code=400, detail=f"Weather API error: {http_err}")
    except Exception as e:
        logger.error(f"Weather API fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Weather API fetch failed: {e}")

# -------------------------
# Feature engineering
# -------------------------
def preprocess_input(df: pd.DataFrame) -> pd.DataFrame:
    df["hour_of_day"] = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.dayofweek
    df["month"] = df["datetime"].dt.month
    return df

# -------------------------
# Impact equivalents
# -------------------------
def format_tree_message(trees: float) -> str:
    if trees < 0.5:
        return "You helped a sapling take root 🌱"
    elif trees < 1.5:
        return "You planted a tree today 🌳"
    elif trees < 3:
        return "You planted two trees 🌳🌳"
    elif trees < 5:
        return "You grew a small grove 🌲🌳🌲"
    elif trees < 10:
        return "You restored a patch of forest 🌳🌳🌳🌳🌳"
    else:
        return "You made a forest flourish 🌳🌲🌳🌲🌳"

def calculate_impact(avg_score: float, best_score: float, duration_hours: int) -> dict:
    co2_saved_kg = max(0, (best_score - avg_score) / 10.0) * duration_hours
    trees_planted = round(co2_saved_kg / 21.77, 2)
    return {
        "trees_planted_equiv": trees_planted,
        "tree_message": format_tree_message(trees_planted)
    }

# -------------------------
# Main Prediction Function
# -------------------------
async def generate_predictions(
    location: str,
    hours_ahead: int = 24,
    day: Optional[str] = None,
    duration_hours: int = 1
) -> dict:
    try:
        lat, lon = geocode_location(location)
        weather_df = get_weather_forecast(lat, lon, hours_ahead=168)

        df_proc = preprocess_input(weather_df)
        X = df_proc[features]
        dmat = xgb.DMatrix(X)
        df_proc["predicted_score"] = model.predict(dmat)

        max_score = df_proc["predicted_score"].max()
        min_score = df_proc["predicted_score"].min()
        df_proc["cleanliness_score"] = ((df_proc["predicted_score"] - min_score) /
                                        (max_score - min_score) * 100).round(1)

        if day:
            target_date = pd.to_datetime(day).date()
            df_proc = df_proc[df_proc["datetime"].dt.date == target_date]
            if df_proc.empty:
                raise HTTPException(status_code=404, detail=f"No forecast data for {day}")

        scores = df_proc["cleanliness_score"].tolist()
        best_start_idx = 0
        best_avg = -1
        for i in range(len(scores) - duration_hours + 1):
            avg_window = sum(scores[i:i+duration_hours]) / duration_hours
            if avg_window > best_avg:
                best_avg = avg_window
                best_start_idx = i

        best_block = df_proc.iloc[best_start_idx:best_start_idx+duration_hours]
        impact = calculate_impact(avg_score=sum(scores)/len(scores),
                                  best_score=best_avg,
                                  duration_hours=duration_hours)

        prediction_points = [
            PredictionPoint(
                timestamp=row["datetime"],
                cleanliness_score=row["cleanliness_score"],
                confidence=None,
                carbon_intensity=None
            )
            for _, row in df_proc.iterrows()
        ]

        return {
            "location": location,
            "generated_at": datetime.utcnow(),
            "predictions": prediction_points,
            "recommended_window": {
                "start": best_block.iloc[0]["datetime"],
                "end": best_block.iloc[-1]["datetime"],
                "average_cleanliness_score": round(best_avg, 1),
                "impact": impact
            },
            "model_version": MODEL_VERSION,
            "data_freshness": "live"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))