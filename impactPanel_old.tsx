import React from 'react'
import { TreePine, Car, Factory } from 'lucide-react'
import type { ImpactResponse } from '@shared/types'

interface ImpactPanelProps {
  impact: ImpactResponse
}

const ImpactPanel: React.FC<ImpactPanelProps> = ({ impact }) => {
  const { cleanest_hour_impact, dirtiest_hour_impact, potential_savings } = impact

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="text-center p-4 bg-primary-50 rounded-lg border border-primary-200">
        <h4 className="text-lg font-semibold text-primary-900 mb-2">
          Potential Environmental Impact
        </h4>
        <p className="text-primary-700">
          By using {impact.usage_kwh} kWh during the cleanest hour instead of the dirtiest hour, 
          you could save <strong>{potential_savings.co2_saved_kg} kg of CO₂</strong>
        </p>
      </div>

      {/* Impact Metrics Grid */}
      <div className="grid md:grid-cols-3 gap-4">
        {/* Trees Equivalent */}
        <div className="impact-card rounded-lg p-4 text-center">
          <div className="flex justify-center mb-3">
            <TreePine className="h-8 w-8 text-primary-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            {potential_savings.trees_equivalent}
          </div>
          <div className="text-sm text-gray-600 mb-2">
            Trees planted equivalent
          </div>
          <div className="text-xs text-gray-500">
            Based on annual CO₂ absorption
          </div>
        </div>

        {/* Car Kilometers */}
        <div className="impact-card rounded-lg p-4 text-center">
          <div className="flex justify-center mb-3">
            <Car className="h-8 w-8 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            {Math.round(potential_savings.car_km_avoided)}
          </div>
          <div className="text-sm text-gray-600 mb-2">
            Car kilometers avoided
          </div>
          <div className="text-xs text-gray-500">
            Equivalent driving distance
          </div>
        </div>

        {/* Coal Plant Hours */}
        <div className="impact-card rounded-lg p-4 text-center">
          <div className="flex justify-center mb-3">
            <Factory className="h-8 w-8 text-gray-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            {potential_savings.coal_plants_offset_hours.toFixed(3)}
          </div>
          <div className="text-sm text-gray-600 mb-2">
            Coal plant hours offset
          </div>
          <div className="text-xs text-gray-500">
            Equivalent power generation
          </div>
        </div>
      </div>

      {/* Detailed Comparison */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Cleanest Hour */}
        <div className="border border-primary-200 rounded-lg p-4">
          <div className="flex items-center mb-3">
            <div className="w-3 h-3 bg-primary-500 rounded-full mr-2"></div>
            <h5 className="font-semibold text-gray-900">Cleanest Hour Impact</h5>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">CO₂ Emissions:</span>
              <span className="font-medium">{cleanest_hour_impact.co2_saved_kg} kg</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Trees Equivalent:</span>
              <span className="font-medium">{cleanest_hour_impact.trees_equivalent}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Car Distance:</span>
              <span className="font-medium">{Math.round(cleanest_hour_impact.car_km_avoided)} km</span>
            </div>
          </div>
        </div>

        {/* Dirtiest Hour */}
        <div className="border border-secondary-200 rounded-lg p-4">
          <div className="flex items-center mb-3">
            <div className="w-3 h-3 bg-secondary-500 rounded-full mr-2"></div>
            <h5 className="font-semibold text-gray-900">Dirtiest Hour Impact</h5>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">CO₂ Emissions:</span>
              <span className="font-medium">{dirtiest_hour_impact.co2_saved_kg} kg</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Trees Equivalent:</span>
              <span className="font-medium">{dirtiest_hour_impact.trees_equivalent}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Car Distance:</span>
              <span className="font-medium">{Math.round(dirtiest_hour_impact.car_km_avoided)} km</span>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="text-center p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600">
          💡 <strong>Tip:</strong> Schedule your high-energy activities (laundry, charging, heating) 
          during green hours to maximize your environmental impact!
        </p>
      </div>
    </div>
  )
}

export default ImpactPanel