import React from 'react'
import Timeline from './Timeline'
import ImpactPanel from './ImpactPanel'
import LocationSelector from './LocationSelector'
import LoadingSpinner from '../Common/LoadingSpinner'
import { usePredictions } from '../../hooks/usePredictions'
import { useImpactMetrics } from '../../hooks/useImpactMetrics'
import { useState } from 'react'

const Dashboard: React.FC = () => {
  const [selectedLocation, setSelectedLocation] = useState('default')
  const [energyUsage, setEnergyUsage] = useState(1.0)

  const { 
    data: predictions, 
    isLoading: predictionsLoading, 
    error: predictionsError 
  } = usePredictions(selectedLocation)

  const { 
    data: impact, 
    isLoading: impactLoading, 
    error: impactError 
  } = useImpactMetrics(selectedLocation, energyUsage)

  if (predictionsLoading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <LoadingSpinner />
      </div>
    )
  }

  if (predictionsError) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Unable to load predictions</h3>
        <p className="text-gray-500">Please try again later or select a different location.</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Clean Energy Dashboard
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Discover the cleanest hours for electricity usage and minimize your carbon footprint.
          Green hours represent the cleanest energy, while red hours have higher carbon intensity.
        </p>
      </div>

      {/* Location and Usage Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-center">
        <LocationSelector
          selectedLocation={selectedLocation}
          onLocationChange={setSelectedLocation}
        />
        
        <div className="flex items-center space-x-2">
          <label htmlFor="energy-usage" className="text-sm font-medium text-gray-700">
            Energy Usage:
          </label>
          <input
            id="energy-usage"
            type="number"
            min="0.1"
            max="100"
            step="0.1"
            value={energyUsage}
            onChange={(e) => setEnergyUsage(parseFloat(e.target.value) || 1.0)}
            className="input-field w-20"
          />
          <span className="text-sm text-gray-500">kWh</span>
        </div>
      </div>

      {/* Timeline Section */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">
          24-Hour Clean Energy Timeline
        </h3>
        {predictions && (
          <Timeline predictions={predictions.predictions} />
        )}
      </div>

      {/* Impact Metrics Section */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">
          Environmental Impact
        </h3>
        {impactLoading ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        ) : impactError ? (
          <div className="text-center py-8 text-gray-500">
            Unable to calculate impact metrics
          </div>
        ) : impact ? (
          <ImpactPanel impact={impact} />
        ) : null}
      </div>

      {/* Information Section */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h4 className="text-lg font-semibold text-gray-900 mb-3">
            How It Works
          </h4>
          <ul className="space-y-2 text-gray-600">
            <li className="flex items-start">
              <span className="text-primary-500 mr-2">•</span>
              Real-time data from environmental and grid sources
            </li>
            <li className="flex items-start">
              <span className="text-primary-500 mr-2">•</span>
              AI predictions for the next 24 hours
            </li>
            <li className="flex items-start">
              <span className="text-primary-500 mr-2">•</span>
              Cleanliness scores from 0-100 (higher is cleaner)
            </li>
            <li className="flex items-start">
              <span className="text-primary-500 mr-2">•</span>
              Updated hourly with fresh predictions
            </li>
          </ul>
        </div>

        <div className="card">
          <h4 className="text-lg font-semibold text-gray-900 mb-3">
            Tips for Clean Energy Use
          </h4>
          <ul className="space-y-2 text-gray-600">
            <li className="flex items-start">
              <span className="text-primary-500 mr-2">•</span>
              Schedule high-energy activities during green hours
            </li>
            <li className="flex items-start">
              <span className="text-primary-500 mr-2">•</span>
              Avoid red hours for non-essential energy use
            </li>
            <li className="flex items-start">
              <span className="text-primary-500 mr-2">•</span>
              Consider battery storage during clean periods
            </li>
            <li className="flex items-start">
              <span className="text-primary-500 mr-2">•</span>
              Enable notifications for optimal timing alerts
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Dashboard