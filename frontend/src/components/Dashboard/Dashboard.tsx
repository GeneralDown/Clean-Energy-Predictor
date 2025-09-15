import React, { useState } from 'react'
import TimelineGraph from './TimelineGraph'
import ImpactPanel from './ImpactPanel'
import LocationSelector from './LocationSelector'
import LoadingSpinner from '../Common/LoadingSpinner'
import { usePredictions } from '../../hooks/usePredictions'

const Dashboard: React.FC = () => {
  const [locationInput, setLocationInput] = useState('default')
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null)
  const [durationInput, setDurationInput] = useState('1')
  const [durationHours, setDurationHours] = useState(1)

  const { data: predictions, isLoading: predictionsLoading, error: predictionsError } =
    usePredictions(selectedLocation ?? '', undefined, durationHours)

  const handleLoad = () => {
    const parsedHours = parseInt(durationInput)
    setDurationHours(isNaN(parsedHours) ? 1 : Math.max(1, parsedHours))
    setSelectedLocation(locationInput.trim())
  }

  if (predictionsLoading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <LoadingSpinner />
      </div>
    )
  }

  if (predictionsError && selectedLocation) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <svg
            className="mx-auto h-12 w-12"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Unable to load predictions
        </h3>
        <p className="text-gray-500">
          Please try again later or select a different location.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Clean Energy Dashboard
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Discover the cleanest hours for electricity usage and minimize your carbon footprint.
        </p>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-center">
        <LocationSelector
          selectedLocation={locationInput}
          onLocationChange={setLocationInput}
        />

        <div className="flex items-center space-x-2">
          <label htmlFor="duration-hours" className="text-sm font-medium text-gray-700">
            Duration:
          </label>
          <input
            id="duration-hours"
            type="number"
            min="1"
            max="24"
            step="1"
            value={durationInput}
            onChange={(e) => setDurationInput(e.target.value)}
            className="input-field w-20"
          />
          <span className="text-sm text-gray-500">hours</span>
        </div>

        <button
          onClick={handleLoad}
          disabled={!locationInput.trim() || !durationInput.trim()}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          Load
        </button>
      </div>

      {/* Graph */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">
          24-Hour Clean Energy Graph
        </h3>
        {predictions && (
          <TimelineGraph
            predictions={predictions.predictions}
            recommendedWindow={
              predictions.recommended_window
                ? {
                    start: predictions.recommended_window.start,
                    end: predictions.recommended_window.end,
                    avg_score: predictions.recommended_window.average_cleanliness_score,
                    average_cleanliness_score: predictions.recommended_window.average_cleanliness_score,
                    impact: predictions.recommended_window.impact
                  }
                : undefined
            }
          />
        )}
      </div>

      {/* Impact */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">
          Environmental Impact
        </h3>
        {predictions && predictions.recommended_window?.impact ? (
          <ImpactPanel impact={predictions.recommended_window.impact} />
        ) : (
          <div className="text-center py-8 text-gray-500">
            No impact data available
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard