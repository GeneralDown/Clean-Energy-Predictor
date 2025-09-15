# Clean Energy Predictor

A full-stack web application that helps users identify the cleanest hours of the day for electricity usage by analyzing real-time environmental and grid data.

## Project Structure

```
clean-energy-predictor/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/            # Pydantic data models
│   │   │   ├── __init__.py
│   │   │   ├── environmental.py
│   │   │   ├── grid.py
│   │   │   └── prediction.py
│   │   ├── services/          # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── data_ingestion.py
│   │   │   └── prediction.py
│   │   └── api/              # API routes
│   │       ├── __init__.py
│   │       └── routes/
│   │           ├── predictions.py
│   │           ├── impact.py
│   │           ├── locations.py
│   │           └── notifications.py
│   ├── tests/                # Backend tests
│   │   ├── __init__.py
│   │   ├── test_main.py
│   │   └── test_models.py
│   ├── main.py              # FastAPI entry point
│   ├── requirements.txt     # Python dependencies
│   ├── pyproject.toml      # Python project config
│   └── .flake8            # Linting configuration
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Dashboard/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── Timeline.tsx
│   │   │   │   ├── ImpactPanel.tsx
│   │   │   │   └── LocationSelector.tsx
│   │   │   └── Common/
│   │   │       ├── LoadingSpinner.tsx
│   │   │       └── ErrorBoundary.tsx
│   │   ├── hooks/        # Custom React hooks
│   │   │   ├── usePredictions.ts
│   │   │   ├── useImpactMetrics.ts
│   │   │   ├── useLocations.ts
│   │   │   └── useNotifications.ts
│   │   ├── services/     # API client
│   │   │   └── api.ts
│   │   ├── utils/        # Utility functions
│   │   │   ├── colorMapping.ts
│   │   │   └── impactCalculations.ts
│   │   ├── test/         # Frontend tests
│   │   │   ├── setup.ts
│   │   │   ├── Dashboard.test.tsx
│   │   │   └── Timeline.test.tsx
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .eslintrc.cjs
│   ├── .prettierrc
│   └── index.html
├── shared/                # Shared TypeScript types
│   └── types/
│       └── index.ts
└── README.md
```

## Features

- **24-Hour Predictions**: AI-powered cleanliness scores for the next 24 hours
- **Interactive Timeline**: Color-coded visualization of clean vs dirty energy periods
- **Environmental Impact**: Calculate CO₂ savings in relatable terms (trees, car km, etc.)
- **Location Support**: Multiple geographic regions with location-specific data
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Updates**: Automatic data refresh and live predictions

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM
- **PostgreSQL**: Primary database
- **Prophet/Scikit-learn**: Machine learning models
- **Pytest**: Testing framework

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
- PostgreSQL (for production)

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

- `GET /api/v1/predictions` - Get 24-hour cleanliness predictions
- `GET /api/v1/impact` - Calculate environmental impact metrics
- `GET /api/v1/locations` - Get supported locations
- `POST /api/v1/notifications/subscribe` - Subscribe to notifications

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
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
- **Backend**: Render, Heroku, or similar Python hosting
- **Frontend**: Vercel, Netlify, or similar static hosting
- **Database**: PostgreSQL on cloud providers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run linting and tests
6. Submit a pull request

## License

This project is licensed under the MIT License.