import React from 'react'
import { TreePine } from 'lucide-react'

interface ImpactPanelProps {
  impact: any
}

const ImpactPanel: React.FC<ImpactPanelProps> = ({ impact }) => {
  // If coming from /predictions
  if ('tree_message' in impact) {
    return (
      <div className="p-4 bg-green-50 rounded-lg text-center">
        <p className="text-lg font-semibold">{impact.tree_message}</p>
        <p className="text-sm text-gray-600">
          Equivalent to planting {impact.trees_planted_equiv} trees
        </p>
      </div>
    )
  }

  // Otherwise, fallback to original /impact layout
  return (
    <div className="p-4 bg-primary-50 rounded-lg border border-primary-200 text-center">
      <h4 className="text-lg font-semibold text-primary-900 mb-2">
        Potential Environmental Impact
      </h4>
      <p className="text-primary-700">
        By using {impact.usage_kwh} kWh during the cleanest hour instead of the
        dirtiest hour, you could save{' '}
        <strong>{impact.potential_savings.co2_saved_kg} kg of CO₂</strong>
      </p>
    </div>
  )
}

export default ImpactPanel