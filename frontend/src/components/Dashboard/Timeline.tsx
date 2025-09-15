import React from 'react'
import { format } from 'date-fns'
import { getScoreLabel } from '../../utils/colorMapping'
import type { PredictionPoint } from '@shared/types'

interface TimelineProps {
  predictions: PredictionPoint[]
  recommendedWindow?: { start: string; end: string }
}

const Timeline: React.FC<TimelineProps> = ({ predictions, recommendedWindow }) => {
  const isInWindow = (timestamp: string) => {
    if (!recommendedWindow) return false

    const ts = new Date(timestamp).getTime()
    const start = new Date(recommendedWindow.start).getTime()

    // Find the absolute difference in ms
    const diff = Math.abs(ts - start)
    const oneHour = 60 * 60 * 1000

    // Highlight if within ±30 minutes of the recommended start
    return diff <= oneHour / 2
  }

  return (
    <div className="w-full">
      {/* Desktop Timeline */}
      <div className="hidden md:block">
        <div className="grid grid-cols-12 gap-2">
          {predictions.slice(0, 12).map((p, i) => (
            <TimelineHour key={i} prediction={p} highlight={isInWindow(p.timestamp)} />
          ))}
        </div>
        <div className="grid grid-cols-12 gap-2 mt-2">
          {predictions.slice(12, 24).map((p, i) => (
            <TimelineHour key={i + 12} prediction={p} highlight={isInWindow(p.timestamp)} />
          ))}
        </div>
      </div>

      {/* Mobile Timeline */}
      <div className="md:hidden">
        {[0, 6, 12, 18].map((startIdx) => (
          <div key={startIdx} className="grid grid-cols-6 gap-2 mt-2">
            {predictions.slice(startIdx, startIdx + 6).map((p, i) => (
              <TimelineHour
                key={startIdx + i}
                prediction={p}
                compact
                highlight={isInWindow(p.timestamp)}
              />
            ))}
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-6 flex flex-wrap justify-center gap-4 text-sm">
        <div className="flex items-center">
          <div className="w-4 h-4 bg-primary-500 rounded mr-2"></div>
          <span>Clean (70-100)</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-yellow-500 rounded mr-2"></div>
          <span>Moderate (40-69)</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-secondary-500 rounded mr-2"></div>
          <span>Dirty (0-39)</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 ring-2 ring-green-400 rounded mr-2"></div>
          <span>Best Window</span>
        </div>
      </div>
    </div>
  )
}

interface TimelineHourProps {
  prediction: PredictionPoint
  compact?: boolean
  highlight?: boolean
}

const TimelineHour: React.FC<TimelineHourProps> = ({
  prediction,
  compact = false,
  highlight = false
}) => {
  const label = getScoreLabel(prediction.cleanliness_score)
  const time = format(new Date(prediction.timestamp), 'HH:mm')
  const hour = format(new Date(prediction.timestamp), 'HH')

  return (
    <div className="group relative">
      <div
        className={`
          timeline-hour rounded-lg text-center cursor-pointer
          ${compact ? 'p-2' : 'p-3'}
          ${highlight ? 'ring-4 ring-green-400 ring-offset-2 shadow-lg shadow-green-300' : ''}
        `}
        style={{
          backgroundColor: `hsl(${getScoreHue(prediction.cleanliness_score)}, 70%, 50%)`,
        }}
      >
        <div className="text-white font-semibold">{compact ? hour : time}</div>
        {!compact && (
          <div className="text-white text-xs mt-1 opacity-90">
            {Math.round(prediction.cleanliness_score)}
          </div>
        )}
      </div>

      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 whitespace-nowrap">
        <div className="font-semibold">{time}</div>
        <div>Score: {Math.round(prediction.cleanliness_score)}/100</div>
        <div>Status: {label}</div>
        {prediction.confidence && (
          <div>Confidence: {Math.round(prediction.confidence * 100)}%</div>
        )}
        {prediction.carbon_intensity && (
          <div>CO₂: {Math.round(prediction.carbon_intensity)} g/kWh</div>
        )}
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
      </div>
    </div>
  )
}

// Helper function to convert score to hue (0-360)
const getScoreHue = (score: number): number => {
  if (score <= 39) {
    return 0 + (score / 39) * 20 // 0 to 20
  } else if (score <= 69) {
    return 20 + ((score - 40) / 29) * 40 // 20 to 60
  } else {
    return 60 + ((score - 70) / 30) * 60 // 60 to 120
  }
}

export default Timeline