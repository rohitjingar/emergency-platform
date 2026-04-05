import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { notificationsAPI } from '../../api/notifications'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import Spinner from '../../components/common/Spinner'
import { Bell, CheckCircle } from 'lucide-react'

export default function Notifications() {
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsAPI.getMy(),
    refetchInterval: 10000,
  })

  const markReadMutation = useMutation({
    mutationFn: (id) => notificationsAPI.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications'])
    },
  })

  const notifications = data?.data?.notifications || []
  const unreadCount = notifications.filter(n => !n.is_read).length

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Notifications</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {unreadCount > 0 ? `${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}` : 'All caught up'}
          </p>
        </div>
      </div>

      {error && (
        <Card className="text-center py-8 text-red-600">
          Failed to load notifications
        </Card>
      )}

      {notifications.length === 0 ? (
        <Card className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
            <Bell className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No notifications</h3>
          <p className="text-gray-600 dark:text-gray-400">You're all caught up!</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {notifications.map((notification) => (
            <Card
              key={notification.id}
              className={`transition-all ${
                !notification.is_read ? 'border-l-4 border-l-primary-500 bg-primary-50/30' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className={`
                    w-2 h-2 rounded-full mt-2
                    ${notification.is_read ? 'bg-gray-300' : 'bg-primary-500'}
                  `} />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white capitalize">{notification.type.replace(/_/g, ' ')}</p>
                    <p className="text-gray-600 dark:text-gray-400 mt-1">{notification.message}</p>
                    <p className="text-sm text-gray-400 mt-2">
                      {new Date(notification.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                {!notification.is_read && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => markReadMutation.mutate(notification.id)}
                    loading={markReadMutation.isPending}
                  >
                    <CheckCircle className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
