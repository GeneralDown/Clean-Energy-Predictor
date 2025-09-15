/**
 * React Query hook for fetching energy cleanliness predictions
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../services/api'
import type { PredictionsResponse } from '@shared/types'

export const usePredictions = (location: string = 'default') => {
  return useQuery<PredictionsResponse, Error>({
    queryKey: ['predictions', location],
    queryFn: () => apiClient.getPredictions(location),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 15 * 60 * 1000, // Refetch every 15 minutes
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })
}