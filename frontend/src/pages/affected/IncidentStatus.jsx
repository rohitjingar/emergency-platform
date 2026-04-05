import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { MapContainer, TileLayer, Marker } from 'react-leaflet'
import { incidentsAPI } from '../../api/incidents'
import Card from '../../components/common/Card'
import Spinner from '../../components/common/Spinner'
import Alert from '../../components/common/Alert'
import { SeverityBadge, StatusBadge } from '../../components/common/Badge'
import { MapPin, Clock, User, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import L from 'leaflet'
import { useAuth } from '../../context/AuthContext'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

export default function IncidentStatus() {
  const { id } = useParams()
  const { user } = useAuth()

  const { data, isLoading, error } = useQuery({
    queryKey: ['incident-status', id],
    queryFn: () => incidentsAPI.getStatus(id),
    refetchInterval: 3000,
    refetchIntervalInBackground: false,
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert type="error">
        Failed to load incident details
      </Alert>
    )
  }

  const status = data?.data
  if (!status) return null

  const getStatusStep = (status) => {
    const steps = ['open', 'triaging', 'searching', 'pending_assignment', 'assigned']
    return steps.indexOf(status)
  }

  const currentStep = getStatusStep(status.status)

  const statusSteps = [
    { key: 0, label: 'Reported', icon: AlertTriangle },
    { key: 1, label: 'AI Triage', icon: AlertTriangle },
    { key: 2, label: 'Finding Help', icon: User },
    { key: 3, label: 'Notified', icon: User },
    { key: 4, label: 'Assigned', icon: CheckCircle },
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500 mb-4">
        <Link to="/my-incidents" className="hover:text-primary-600">My Incidents</Link>
        <span>/</span>
        <span>Incident #{id}</span>
      </div>

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Incident Status</h1>
        <StatusBadge status={status.status} />
      </div>

      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          {statusSteps.map((step, index) => {
            const Icon = step.icon
            const isActive = index <= currentStep
            const isCurrent = index === currentStep
            return (
              <div key={step.key} className="flex-1 relative">
                <div className="flex flex-col items-center">
                  <div className={`
                    w-10 h-10 rounded-full flex items-center justify-center
                    ${isActive ? 'bg-primary-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500'}
                    ${isCurrent ? 'ring-4 ring-primary-200' : ''}
                  `}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className={`text-xs mt-2 ${isActive ? 'text-primary-600' : 'text-gray-400 dark:text-gray-500'}`}>
                    {step.label}
                  </span>
                </div>
                {index < statusSteps.length - 1 && (
                  <div className={`
                    absolute top-5 left-1/2 w-full h-0.5 -z-10
                    ${index < currentStep ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'}
                  `} />
                )}
              </div>
            )
          })}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <Card title="Incident Details">
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-500 dark:text-gray-400 dark:text-gray-500">Severity</label>
              <div className="mt-1">
                <SeverityBadge severity={status.severity} />
              </div>
            </div>
            <div>
              <label className="text-sm text-gray-500 dark:text-gray-400 dark:text-gray-500">AI Confidence</label>
              <div className="mt-1">
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all"
                      style={{ width: `${(status.confidence || 0) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">{(status.confidence || 0).toFixed(1)}%</span>
                </div>
              </div>
            </div>
            <div>
              <label className="text-sm text-gray-500 dark:text-gray-400 dark:text-gray-500">Assignment Attempts</label>
              <p className="mt-1 font-medium">{status.assignment_attempts || 0}</p>
            </div>
            {status.fallback_used && (
              <Alert type="warning">
                AI fallback mode was used (confidence capped)
              </Alert>
            )}
          </div>
        </Card>

        <Card title="Volunteer Assignment">
          {status.assigned_volunteer_id ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                <CheckCircle className="h-8 w-8 text-green-600" />
                <div>
                  <p className="font-medium text-green-900">Volunteer Assigned</p>
                  <p className="text-sm text-green-700">ID: {status.assigned_volunteer_id}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-6">
              <User className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 dark:text-gray-400 dark:text-gray-500">Waiting for volunteer assignment</p>
              <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                {status.status === 'searching' ? 'Finding nearby volunteers...' : 'Will be assigned soon'}
              </p>
            </div>
          )}
        </Card>
      </div>

      <Card title="Location">
        <div className="h-64 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
          <MapContainer
            center={[status.latitude || status.incident_id?.latitude || 26.9124, status.longitude || status.incident_id?.longitude || 75.7873]}
            zoom={15}
            className="h-full w-full"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <Marker position={[status.latitude || 26.9124, status.longitude || 75.7873]} />
          </MapContainer>
        </div>
      </Card>
    </div>
  )
}
