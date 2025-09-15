/**
 * API client for Clean Energy Predictor backend
 */

import axios, { AxiosResponse } from 'axios'
import type {
  PredictionsResponse,
  ImpactResponse,
  LocationsResponse,
  NotificationSubscription,
  SubscriptionResponse
} from '@shared/types'

// Create axios instance with base configuration
const api = axios.create({
  baseURL:
    process.env.NODE_ENV === 'production'
      ? 'https://your-api-domain.com/api/v1'
      : 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth tokens (if needed)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
    }
    return Promise.reject(error)
  }
)

// API functions
export const apiClient = {
  // Predictions
  async getPredictions(
    location: string,
    day?: string,
    duration_hours: number = 1
  ): Promise<PredictionsResponse> {
    const response: AxiosResponse<PredictionsResponse> = await api.get(
      '/predictions',
      {
        params: {
          location,
          ...(day ? { day } : {}),
          duration_hours,
        },
      }
    )
    return response.data
  },

  // Impact metrics (kept for future use)
  async getImpactMetrics(
    location: string = 'default',
    usage_kwh: number = 1.0
  ): Promise<ImpactResponse> {
    const response: AxiosResponse<ImpactResponse> = await api.get('/impact', {
      params: { location, usage_kwh },
    })
    return response.data
  },

  // Locations
  async getLocations(): Promise<LocationsResponse> {
    const response: AxiosResponse<LocationsResponse> = await api.get(
      '/locations'
    )
    return response.data
  },

  async getLocationInfo(locationCode: string): Promise<LocationInfo> {
    const response: AxiosResponse<LocationInfo> = await api.get(
      `/locations/${locationCode}`
    )
    return response.data
  },

  // Notifications
  async subscribeNotifications(
    subscription: NotificationSubscription
  ): Promise<SubscriptionResponse> {
    const response: AxiosResponse<SubscriptionResponse> = await api.post(
      '/notifications/subscribe',
      subscription
    )
    return response.data
  },

  async getUserSubscriptions(
    userId: string
  ): Promise<{ subscriptions: SubscriptionResponse[]; total_count: number }> {
    const response = await api.get(`/notifications/subscriptions/${userId}`)
    return response.data
  },

  async updateSubscription(
    subscriptionId: string,
    subscription: NotificationSubscription
  ): Promise<SubscriptionResponse> {
    const response: AxiosResponse<SubscriptionResponse> = await api.put(
      `/notifications/subscriptions/${subscriptionId}`,
      subscription
    )
    return response.data
  },

  async unsubscribeNotifications(
    subscriptionId: string
  ): Promise<{ status: string; timestamp: string }> {
    const response = await api.delete(
      `/notifications/subscriptions/${subscriptionId}`
    )
    return response.data
  },

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await api.get('/health')
    return response.data
  },
}

export default api