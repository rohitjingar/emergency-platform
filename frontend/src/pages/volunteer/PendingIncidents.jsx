import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { volunteersAPI } from '../../api/volunteers'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import Spinner from '../../components/common/Spinner'
import Alert from '../../components/common/Alert'
import Modal from '../../components/common/Modal'
import { SeverityBadge } from '../../components/common/Badge'
import { MapPin, Clock, CheckCircle, XCircle, AlertCircle, UserPlus } from 'lucide-react'

const DECLINE_OPTIONS = [
  { value: 30, label: '30 minutes' },
  { value: 60, label: '1 hour' },
  { value: 120, label: '2 hours' },
]

export default function PendingIncidents() {
  const queryClient = useQueryClient()
  const [declineModal, setDeclineModal] = useState(null)

  const { data: profileData, isLoading: profileLoading, error: profileError } = useQuery({
    queryKey: ['volunteer-profile'],
    queryFn: () => volunteersAPI.getProfile(),
    retry: false,
  })

  const hasProfile = profileData && !profileError

  const { data, isLoading, error } = useQuery({
    queryKey: ['pending-incidents'],
    queryFn: () => volunteersAPI.getPending(),
    refetchInterval: 3000,
    refetchIntervalInBackground: false,
    enabled: hasProfile,
  })

  const acceptMutation = useMutation({
    mutationFn: (id) => volunteersAPI.acceptIncident(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['pending-incidents'])
    },
  })

  const declineMutation = useMutation({
    mutationFn: ({ id, minutes }) => volunteersAPI.declineIncident(id, { unavailable_minutes: minutes }),
    onSuccess: () => {
      queryClient.invalidateQueries(['pending-incidents'])
      setDeclineModal(null)
    },
  })

  if (profileLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!hasProfile) {
    return (
      <div className="max-w-md mx-auto">
        <Card className="text-center">
          <div className="py-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
              <UserPlus className="h-8 w-8 text-primary-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Create Profile First</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              You need to register your volunteer profile before you can receive and respond to incidents.
            </p>
            <Link to="/volunteer/register">
              <Button>
                <UserPlus className="h-4 w-4 mr-2" />
                Register Profile
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    )
  }

  const pendingIncidents = data?.data?.pending_incidents || []
  const count = data?.data?.count || 0

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Pending Incidents</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">You have {count} incident(s) waiting for response</p>
        </div>
        {count > 0 && (
          <div className="flex items-center gap-2 px-4 py-2 bg-yellow-100 text-yellow-800 rounded-lg">
            <AlertCircle className="h-5 w-5" />
            <span className="font-medium">Respond within 60 seconds</span>
          </div>
        )}
      </div>

      {error && (
        <Alert type="error" className="mb-6">
          Failed to load pending incidents
        </Alert>
      )}

      {count === 0 ? (
        <Card className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No pending incidents</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">You're all caught up! We'll notify you when a new incident is assigned to you.</p>
          <Link to="/volunteer/map">
            <Button variant="outline">
              Update Your Status
            </Button>
          </Link>
        </Card>
      ) : (
        <div className="space-y-4">
          {pendingIncidents.map((incident) => (
            <Card key={incident.incident_id} className="border-l-4 border-l-yellow-500">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <h3 className="font-semibold text-lg text-gray-900 dark:text-white capitalize">{incident.type}</h3>
                    <SeverityBadge severity={incident.severity} />
                  </div>
                  
                  <p className="text-gray-600 dark:text-gray-400 mb-4">{incident.description}</p>
                  
                  <div className="flex items-center gap-6 text-sm text-gray-500 dark:text-gray-400">
                    <span className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {incident.latitude.toFixed(4)}, {incident.longitude.toFixed(4)}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      Assigned {new Date(incident.assigned_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>

                <div className="flex flex-col gap-2 ml-4">
                  <Button
                    variant="success"
                    onClick={() => acceptMutation.mutate(incident.incident_id)}
                    loading={acceptMutation.isPending}
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Accept
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => setDeclineModal(incident.incident_id)}
                    loading={declineMutation.isPending}
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    Decline
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal
        isOpen={!!declineModal}
        onClose={() => setDeclineModal(null)}
        title="Decline Incident"
        footer={
          <>
            <Button variant="secondary" onClick={() => setDeclineModal(null)}>Cancel</Button>
            <Button
              variant="danger"
              onClick={() => declineMutation.mutate({ id: declineModal, minutes: 30 })}
              loading={declineMutation.isPending}
            >
              Confirm Decline
            </Button>
          </>
        }
      >
        <p className="text-gray-600 dark:text-gray-400 mb-4">How long will you be unavailable?</p>
        <div className="space-y-2">
          {DECLINE_OPTIONS.map((option) => (
            <button
              key={option.value}
              className="w-full p-3 text-left border rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
              onClick={() => declineMutation.mutate({ id: declineModal, minutes: option.value })}
              disabled={declineMutation.isPending}
            >
              {option.label}
            </button>
          ))}
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-4">
          The incident will be reassigned to another volunteer.
        </p>
      </Modal>
    </div>
  )
}
