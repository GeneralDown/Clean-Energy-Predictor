/**
 * Utility functions for environmental impact calculations and formatting
 */

import type { ImpactMetrics } from '@shared/types'

// Conversion factors
export const CONVERSION_FACTORS = {
  TREE_CO2_ABSORPTION_KG_YEAR: 22, // kg CO2 per tree per year
  CAR_CO2_EMISSION_KG_KM: 0.12,    // kg CO2 per km for average car
  COAL_PLANT_CO2_KG_HOUR: 820000,  // kg CO2 per hour for average coal plant
} as const

/**
 * Calculate impact metrics from CO2 savings
 */
export const calculateImpactMetrics = (co2SavedKg: number): ImpactMetrics => {
  const treesEquivalent = Math.max(1, Math.round(
    co2SavedKg * 365 / CONVERSION_FACTORS.TREE_CO2_ABSORPTION_KG_YEAR
  ))
  
  const carKmAvoided = co2SavedKg / CONVERSION_FACTORS.CAR_CO2_EMISSION_KG_KM
  
  const coalPlantsOffsetHours = co2SavedKg / CONVERSION_FACTORS.COAL_PLANT_CO2_KG_HOUR

  return {
    co2_saved_kg: Math.round(co2SavedKg * 100) / 100, // Round to 2 decimal places
    trees_equivalent: treesEquivalent,
    car_km_avoided: Math.round(carKmAvoided * 10) / 10, // Round to 1 decimal place
    coal_plants_offset_hours: Math.round(coalPlantsOffsetHours * 10000) / 10000, // Round to 4 decimal places
  }
}

/**
 * Format impact metrics for display
 */
export const formatImpactMetrics = {
  co2: (kg: number): string => `${kg.toFixed(2)} kg CO₂`,
  trees: (count: number): string => `${count} tree${count !== 1 ? 's' : ''}`,
  carDistance: (km: number): string => `${km.toFixed(1)} km`,
  coalPlantHours: (hours: number): string => `${hours.toFixed(4)} hours`,
}

/**
 * Get relative impact description
 */
export const getImpactDescription = (savings: ImpactMetrics): string => {
  if (savings.co2_saved_kg < 0.1) {
    return 'Small but meaningful environmental benefit'
  } else if (savings.co2_saved_kg < 1) {
    return 'Moderate environmental impact reduction'
  } else if (savings.co2_saved_kg < 5) {
    return 'Significant environmental benefit'
  } else {
    return 'Substantial positive environmental impact'
  }
}

/**
 * Calculate percentage improvement
 */
export const calculatePercentageImprovement = (
  cleanestImpact: ImpactMetrics,
  dirtiestImpact: ImpactMetrics
): number => {
  if (dirtiestImpact.co2_saved_kg === 0) return 0
  
  const improvement = (dirtiestImpact.co2_saved_kg - cleanestImpact.co2_saved_kg) / dirtiestImpact.co2_saved_kg
  return Math.round(improvement * 100)
}