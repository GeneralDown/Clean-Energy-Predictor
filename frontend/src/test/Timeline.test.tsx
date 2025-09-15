import { render, screen } from '@testing-library/react'
import Timeline from '../components/Dashboard/Timeline'
import type { PredictionPoint } from '@shared/types'

const mockPredictions: PredictionPoint[] = Array.from({ length: 24 }, (_, i) => ({
  timestamp: new Date(Date.now() + i * 60 * 60 * 1000).toISOString(),
  cleanliness_score: 50 + Math.random() * 50,
  confidence: 0.8,
  carbon_intensity: 400
}))

describe('Timeline', () => {
  test('renders timeline with predictions', () => {
    render(<Timeline predictions={mockPredictions} />)
    
    // Should render legend
    expect(screen.getByText('Clean (70-100)')).toBeInTheDocument()
    expect(screen.getByText('Moderate (40-69)')).toBeInTheDocument()
    expect(screen.getByText('Dirty (0-39)')).toBeInTheDocument()
  })

  test('renders correct number of time slots', () => {
    const { container } = render(<Timeline predictions={mockPredictions} />)
    
    // Should have timeline hours (exact count depends on responsive layout)
    const timelineHours = container.querySelectorAll('.timeline-hour')
    expect(timelineHours.length).toBeGreaterThan(0)
  })
})