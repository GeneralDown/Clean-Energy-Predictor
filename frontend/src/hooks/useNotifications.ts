/**
 * React Query hooks for notification management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../services/api'
import type { NotificationSubscription, SubscriptionResponse } from '@shared/types'

export const useUserSubscriptions = (userId: string) => {
  return useQuery({
    queryKey: ['subscriptions', userId],
    queryFn: () => apiClient.getUserSubscriptions(userId),
    enabled: !!userId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useSubscribeNotifications = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (subscription: NotificationSubscription) => 
      apiClient.subscribeNotifications(subscription),
    onSuccess: (data, variables) => {
      // Invalidate and refetch user subscriptions
      queryClient.invalidateQueries({ queryKey: ['subscriptions', variables.user_id] })
    },
  })
}

export const useUpdateSubscription = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ subscriptionId, subscription }: { 
      subscriptionId: string
      subscription: NotificationSubscription 
    }) => apiClient.updateSubscription(subscriptionId, subscription),
    onSuccess: (data, variables) => {
      // Invalidate and refetch user subscriptions
      queryClient.invalidateQueries({ queryKey: ['subscriptions', variables.subscription.user_id] })
    },
  })
}

export const useUnsubscribeNotifications = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (subscriptionId: string) => 
      apiClient.unsubscribeNotifications(subscriptionId),
    onSuccess: () => {
      // Invalidate all subscription queries
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] })
    },
  })
}