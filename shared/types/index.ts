/**
 * Shared TypeScript interfaces for Clean Energy Predictor
 * These types match the backend Pydantic models
 */

// Environmental Data Types
export interface EnvironmentalData {
  timestamp: string
  location: string
  temperature?: number
  humidity?: number
  wind_speed?: number
  solar_irradiance?: number
  air_quality_index?: number
}

export interface EnvironmentalDataResponse extends EnvironmentalData {
  id: number
  created_at: string
}

// Grid Data Types
export interface GridData {
  timestamp: string
  region: string
  renewable_percentage?: number
  coal_percentage?: number
  natural_gas_percentage?: number
  nuclear_percentage?: number
  total_demand?: number
  carbon_intensity?: number
}

export interface GridDataResponse extends GridData {
  id: number
  created_at: string
}

// Prediction Types
export interface PredictionPoint {
  timestamp: string
  cleanliness_score: number
  // Backend may send null; allow it explicitly
  confidence?: number | null
  carbon_intensity?: number | null
}

// Impact returned specifically inside recommended_window from /predictions
export interface RecommendedWindowImpact {
  trees_planted_equiv?: number
  tree_message?: string
}

export interface PredictionsResponse {
  location: string
  generated_at: string
  predictions: PredictionPoint[]
  recommended_window?: {
    start: string // ISO timestamp
    end: string   // ISO timestamp
    average_cleanliness_score?: number
    impact?: RecommendedWindowImpact
  }
  model_version?: string
  data_freshness?: string
}

export interface PredictionResponse {
  id: number
  location: string
  prediction_timestamp: string
  target_timestamp: string
  cleanliness_score: number
  confidence?: number
  model_version?: string
  created_at: string
}

// Impact Types (other endpoints)
export interface ImpactMetrics {
  co2_saved_kg: number
  trees_equivalent: number
  car_km_avoided: number
  coal_plants_offset_hours: number
}

export interface ImpactResponse {
  location: string
  usage_kwh: number
  cleanest_hour_impact: ImpactMetrics
  dirtiest_hour_impact: ImpactMetrics
  potential_savings: ImpactMetrics
  calculation_timestamp: string
}

// Location Types
export interface LocationInfo {
  code: string
  name: string
  region: string
  timezone: string
  supported_features: string[]
}

export interface LocationsResponse {
  locations: LocationInfo[]
  total_count: number
}

// Notification Types
export interface NotificationSubscription {
  user_id: string
  location: string
  notification_threshold: number
  advance_notice_hours: number
  enabled: boolean
}

export interface SubscriptionResponse extends NotificationSubscription {
  subscription_id: string
  created_at: string
  updated_at: string
}

// API Response Types
export interface ApiError {
  detail: string
  status_code?: number
}

export interface ApiResponse<T> {
  data?: T
  error?: ApiError
  loading: boolean
}