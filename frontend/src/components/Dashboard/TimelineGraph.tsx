import React, { useMemo, useState } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  TimeScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import 'chartjs-adapter-date-fns'
import type { PredictionPoint } from '@shared/types'
import { format } from 'date-fns'

ChartJS.register(
  TimeScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// Plugin to draw a more prominent green shaded best window ON TOP of datasets
const BestWindowPlugin = (start: Date, end: Date) => ({
  id: 'bestWindowHighlight',
  afterDatasetsDraw: (chart: any) => {
    if (!start || !end) return
    const { ctx, chartArea, scales } = chart
    const xScale = scales.x

    const startPixel = xScale.getPixelForValue(start)
    const endPixel = xScale.getPixelForValue(end)

    ctx.save()
    // Increased opacity for stronger visibility
    ctx.fillStyle = 'rgba(34,197,94,0.4)'
    ctx.fillRect(startPixel, chartArea.top, endPixel - startPixel, chartArea.bottom - chartArea.top)

    // Fully opaque border
    ctx.strokeStyle = 'rgba(34,197,94,1)'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(startPixel, chartArea.top)
    ctx.lineTo(startPixel, chartArea.bottom)
    ctx.moveTo(endPixel, chartArea.top)
    ctx.lineTo(endPixel, chartArea.bottom)
    ctx.stroke()
    ctx.restore()
  }
})

interface TimelineGraphProps {
  predictions: PredictionPoint[]
  recommendedWindow?: {
    start: string
    end?: string
    avg_score?: number
    average_cleanliness_score?: number
    impact?: any
  }
}

const TimelineGraph: React.FC<TimelineGraphProps> = ({ predictions, recommendedWindow }) => {
  const [hoverText, setHoverText] = useState<string | null>(null)

  const startDate = recommendedWindow?.start ? new Date(recommendedWindow.start) : undefined
  const endDate = recommendedWindow?.end ? new Date(recommendedWindow.end) : undefined

  const insideTimes = useMemo(() => {
    if (!recommendedWindow) return new Set<string>()
    return new Set(
      predictions
        .filter((p) => p.timestamp >= recommendedWindow.start && p.timestamp <= (recommendedWindow.end ?? ''))
        .map((p) => p.timestamp)
    )
  }, [predictions, recommendedWindow])

  const avgOutsideWindow = useMemo(() => {
    if (!recommendedWindow) return null
    const outsideScores = predictions
      .filter((p) => !insideTimes.has(p.timestamp))
      .map((p) => p.cleanliness_score)
    if (!outsideScores.length) return null
    return outsideScores.reduce((a, b) => a + b, 0) / outsideScores.length
  }, [predictions, insideTimes, recommendedWindow])

  const avgInside = recommendedWindow?.avg_score ?? recommendedWindow?.average_cleanliness_score ?? null

  const data = {
    datasets: [
      {
        label: 'Cleanliness Score',
        data: predictions.map((p) => ({
          x: new Date(p.timestamp),
          y: p.cleanliness_score
        })),
        borderColor: (ctx: any) => {
          const { chart } = ctx
          const { ctx: canvasCtx, chartArea } = chart
          if (!chartArea) return '#3b82f6'

          const gradient = canvasCtx.createLinearGradient(chartArea.left, 0, chartArea.right, 0)
          const minX = predictions[0] ? new Date(predictions[0].timestamp).getTime() : 0
          const maxX = predictions[predictions.length - 1]
            ? new Date(predictions[predictions.length - 1].timestamp).getTime()
            : 1

          predictions.forEach((p) => {
            const ratio = (new Date(p.timestamp).getTime() - minX) / (maxX - minX || 1)
            let color = '#ef4444'
            if (p.cleanliness_score >= 70) color = '#22c55e'
            else if (p.cleanliness_score >= 40) color = '#eab308'
            gradient.addColorStop(ratio, color)
          })

          return gradient
        },
        backgroundColor: (ctx: any) => {
          const { chart } = ctx
          const { ctx: canvasCtx, chartArea } = chart
          if (!chartArea) return null
          const gradient = canvasCtx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
          gradient.addColorStop(0, 'rgba(59,130,246,0.4)')
          gradient.addColorStop(1, 'rgba(59,130,246,0)')
          return gradient
        },
        tension: 0.4,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 5
      }
    ]
  }

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: 'Clean Energy Forecast' },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          label: (ctx: any) => `Score: ${Math.round(ctx.parsed.y)}`
        }
      }
    },
    onHover: (_: any, elements: any) => {
      if (elements.length && recommendedWindow) {
        const idx = elements[0].index
        const time = predictions[idx]?.timestamp
        if (time && insideTimes.has(time)) {
          const co2 = recommendedWindow.impact?.co2_saved_kg
          setHoverText(
            `Optimal period: ${recommendedWindow.start} – ${recommendedWindow.end}, Avg Score: ${avgInside ?? 'N/A'}${
              co2 !== undefined ? `, Saves ~${co2} kg CO₂` : ''
            }`
          )
        } else {
          setHoverText(null)
        }
      } else {
        setHoverText(null)
      }
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'hour' as const,
          displayFormats: { hour: 'MMM d HH:mm' }
        },
        title: { display: true, text: 'Time' },
        grid: { display: false }
      },
      y: {
        min: 0,
        max: 100,
        title: { display: true, text: 'Cleanliness Score' },
        grid: { color: 'rgba(0,0,0,0.05)' }
      }
    }
  }

  return (
    <div className="w-full relative">
      <Line
        data={data}
        options={options}
        plugins={startDate && endDate ? [BestWindowPlugin(startDate, endDate)] : []}
      />
      {hoverText && (
        <div className="absolute top-2 left-2 bg-white border border-gray-300 rounded px-3 py-1 text-sm shadow">
          {hoverText}
        </div>
      )}
      {startDate && endDate && (
        <div className="mt-2 text-center text-green-600 font-semibold">
          Best Window: {format(startDate, 'MMM d HH:mm')} – {format(endDate, 'MMM d HH:mm')}
        </div>
      )}
      {avgOutsideWindow !== null && avgInside !== null && (
        <div className="mt-1 text-center text-gray-600 text-sm">
          Outside this window: Avg Score {avgOutsideWindow.toFixed(1)} — Inside: Avg Score {avgInside.toFixed(1)}
        </div>
      )}
    </div>
  )
}

export default TimelineGraph