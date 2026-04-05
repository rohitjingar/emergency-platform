import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { incidentsAPI } from '../../api/incidents'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import Spinner from '../../components/common/Spinner'
import Alert from '../../components/common/Alert'
import { SeverityBadge, StatusBadge } from '../../components/common/Badge'
import { Plus, MapPin, Clock } from 'lucide-react'

export default function MyIncidents() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['my-incidents'],
    queryFn: () => incidentsAPI.list({ limit: 50 }),
  })

  const incidents = data?.data || []

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
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">My Incidents</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Track the status of your reported emergencies</p>
        </div>
        <Link to="/report">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Report
          </Button>
        </Link>
      </div>

      {error && (
        <Alert type="error" className="mb-6">
          Failed to load incidents
        </Alert>
      )}

      {incidents.length === 0 ? (
        <Card className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
            <MapPin className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No incidents reported</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">You haven't reported any emergencies yet</p>
          <Link to="/report">
            <Button>Report Your First Incident</Button>
          </Link>
        </Card>
      ) : (
        <div className="space-y-4">
          {incidents.map((incident) => (
            <Card key={incident.id} className="hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-gray-900 dark:text-white capitalize">{incident.type}</h3>
                    <SeverityBadge severity={incident.severity} />
                    <StatusBadge status={incident.status} />
                  </div>
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-3 line-clamp-2">{incident.description}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <span className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {incident.latitude.toFixed(4)}, {incident.longitude.toFixed(4)}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {new Date(incident.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
                <Link to={`/incidents/${incident.id}`}>
                  <Button variant="outline" size="sm">View Details</Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
