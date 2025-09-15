import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import Dashboard from '../components/Dashboard/Dashboard'

// Mock the hooks
jest.mock('../hooks/usePredictions', () => ({
  usePredictions: () => ({
    data: {
      location: 'test',
      generated_at: new Date().toISOString(),
      predictions: Array.from({ length: 24 }, (_, i) => ({
        timestamp: new Date(Date.now() + i * 60 * 60 * 1000).toISOString(),
        cleanliness_score: 50 + Math.random() * 50,
        confidence: 0.8,
        carbon_intensity: 400
      }))
    },
    isLoading: false,
    error: null
  })
}))

jest.mock('../hooks/useImpactMetrics', () => ({
  useImpactMetrics: () => ({
    data: {
      location: 'test',
      usage_kwh: 1.0,
      cleanest_hour_impact: {
        co2_saved_kg: 0.2,
        trees_equivalent: 1,
        car_km_avoided: 1.7,
        coal_plants_offset_hours: 0.0002
      },
      dirtiest_hour_impact: {
        co2_saved_kg: 0.6,
        trees_equivalent: 3,
        car_km_avoided: 5.0,
        coal_plants_offset_hours: 0.0007
      },
      potential_savings: {
        co2_saved_kg: 0.4,
        trees_equivalent: 2,
        car_km_avoided: 3.3,
        coal_plants_offset_hours: 0.0005
      },
      calculation_timestamp: new Date().toISOString()
    },
    isLoading: false,
    error: null
  })
}))

jest.mock('../hooks/useLocations', () => ({
  useLocations: () => ({
    data: {
      locations: [
        {
          code: 'default',
          name: 'Default Location',
          region: 'North America',
          timezone: 'UTC',
          supported_features: ['predictions', 'impact']
        }
      ],
      total_count: 1
    },
    isLoading: false,
    error: null
  })
}))

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('Dashboard', () => {
  test('renders dashboard title', () => {
    renderWithProviders(<Dashboard />)
    expect(screen.getByText('Clean Energy Dashboard')).toBeInTheDocument()
  })

  test('renders timeline section', () => {
    renderWithProviders(<Dashboard />)
    expect(screen.getByText('24-Hour Clean Energy Timeline')).toBeInTheDocument()
  })

  test('renders impact section', () => {
    renderWithProviders(<Dashboard />)
    expect(screen.getByText('Environmental Impact')).toBeInTheDocument()
  })

  test('renders information sections', () => {
    renderWithProviders(<Dashboard />)
    expect(screen.getByText('How It Works')).toBeInTheDocument()
    expect(screen.getByText('Tips for Clean Energy Use')).toBeInTheDocument()
  })
})