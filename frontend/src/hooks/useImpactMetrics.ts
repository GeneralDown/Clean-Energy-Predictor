/**
 * React Query hook for fetching environmental impact metrics
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../services/api'
import type { ImpactResponse } from '@shared/types'

export const useImpactMetrics = (location: string = 'default', usage_kwh: number = 1.0) => {
  return useQuery<ImpactResponse, Error>({
    queryKey: ['impact', location, usage_kwh],
    queryFn: () => apiClient.getImpactMetrics(location, usage_kwh),
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
    enabled: usage_kwh > 0, // Only fetch if usage is valid
  })
}