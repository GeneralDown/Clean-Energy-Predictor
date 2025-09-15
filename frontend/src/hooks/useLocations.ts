/**
 * React Query hook for fetching supported locations
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../services/api'
import type { LocationsResponse } from '@shared/types'

export const useLocations = () => {
  return useQuery<LocationsResponse, Error>({
    queryKey: ['locations'],
    queryFn: () => apiClient.getLocations(),
    staleTime: 60 * 60 * 1000, // 1 hour (locations don't change often)
    retry: 2,
  })
}