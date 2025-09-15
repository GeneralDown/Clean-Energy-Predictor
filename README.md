# Clean Energy Predictor

A full-stack web application that helps users identify the cleanest hours of the day for electricity usage by analyzing real-time environmental data using trained ML model.

## Features

- **Live 24‑Hour Predictions** — Generates cleanliness scores for each hour using real‑time weather forecasts and a trained XGBoost ranking model.
- **Interactive Timeline Graph** — Color‑coded view of clean vs. dirty energy periods, with a green highlight band for the optimal usage window.
- **Environmental Impact Panel** — Converts predicted CO₂ savings into relatable equivalents (e.g., trees planted) with friendly, motivational messages 🌱🌳.
- **Location‑Aware Forecasts** — Enter any city or location; backend geocodes it and fetches tailored weather data from public APIs.
- **Optimal Window Recommendation** — Suggests the best continuous time block for clean energy usage based on user‑selected duration.
- **Real‑Time Data Freshness** — Every prediction request fetches the latest weather data, ensuring recommendations are always up to date.

## Technology Stack

### Backend
- **FastAPI** — Modern Python web framework for serving APIs.
- **Pydantic** — Data validation and serialization for request/response models.
- **Async SQLAlchemy** — Structured data handling (currently using in‑memory/static datasets; no external DB in this build).
- **Data Pipeline** — Python scripts to fetch and merge 1 year of historical carbon intensity + weather data from public APIs (UK Carbon Intensity API, Open‑Meteo Weather Archive).
- **Machine Learning** — XGBoost ranking model (`rank:pairwise`) trained on weather + time features to score hours by predicted cleanliness.
- **Joblib** — Model persistence and loading.
- **Requests / Pandas** — API calls, data wrangling, and feature engineering.
- **Pytest** — Backend testing framework.
### Frontend
- **React 18**: UI framework with TypeScript
- **TailwindCSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching
- **Chart.js**: Data visualization
- **Vite**: Build tool and dev server
- **Vitest**: Testing framework

### Shared
- **TypeScript**: Shared type definitions
- **Axios**: HTTP client

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## API Endpoints

- **`GET /api/v1/predictions`**  
  Generates live cleanliness predictions for a given location using:
  - OpenStreetMap Nominatim API for geocoding
  - Open‑Meteo Forecast API for weather data
  - Trained XGBoost ranking model for scoring hours by predicted cleanliness  
  **Query parameters:**
    - `location` *(string, required)* — City or place name (e.g., `"London"`)
    - `hours_ahead` *(int, optional, default=24)* — Forecast horizon in hours
    - `day` *(YYYY-MM-DD, optional)* — Filter predictions to a specific date
    - `duration_hours` *(int, optional, default=1)* — Duration of optimal usage window to recommend

- **`GET /api/v1/impact`**  
  Calculates environmental impact equivalents (e.g., trees planted) based on predicted CO₂ savings for a given usage window.

- **`GET /api/v1/locations`**  
  Returns a list of supported or recently queried locations.

- **`POST /api/v1/notifications/subscribe`**  
  Subscribes a user to clean‑energy usage alerts for their chosen location and preferences.

## Testing

### Backend Tests
```bash
cd backend
pytest
```

## Linting and Formatting

### Backend
```bash
cd backend
black .
flake8 .
mypy .
```

### Frontend
```bash
cd frontend
npm run lint
npm run format
```

## Deployment

The application is designed to be deployed on:

- **Backend**: Render, Railway, Heroku, or similar Python hosting for FastAPI apps.  
  Loads the trained XGBoost model from `models/` and fetches live weather data from public APIs.
- **Frontend**: Vercel, Netlify, or similar static hosting for React + TypeScript builds.
- **Data/Model Storage**: Model `.pkl` file and any static datasets can be stored in the repo, on cloud storage (e.g., AWS S3, Google Cloud Storage), or as build assets.

> **Note:** This build does not require a live database — predictions are generated from live API data combined with the pre‑trained model.
## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run linting and tests
6. Submit a pull request

## License

This project is licensed under the MIT License.
