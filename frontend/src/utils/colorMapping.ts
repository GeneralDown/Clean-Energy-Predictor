/**
 * Utility functions for mapping cleanliness scores to colors and labels
 */

export const getScoreColor = (score: number): string => {
  if (score >= 70) {
    return 'bg-primary-500 text-white'
  } else if (score >= 40) {
    return 'bg-yellow-500 text-white'
  } else {
    return 'bg-secondary-500 text-white'
  }
}

export const getScoreLabel = (score: number): string => {
  if (score >= 70) {
    return 'Clean'
  } else if (score >= 40) {
    return 'Moderate'
  } else {
    return 'Dirty'
  }
}

export const getScoreGradient = (score: number): string => {
  if (score >= 70) {
    return 'timeline-gradient-clean'
  } else if (score >= 40) {
    return 'timeline-gradient-moderate'
  } else {
    return 'timeline-gradient-dirty'
  }
}

export const getScoreTextColor = (score: number): string => {
  // Always return white for good contrast on colored backgrounds
  return 'text-white'
}

export const getScoreBorderColor = (score: number): string => {
  if (score >= 70) {
    return 'border-primary-500'
  } else if (score >= 40) {
    return 'border-yellow-500'
  } else {
    return 'border-secondary-500'
  }
}