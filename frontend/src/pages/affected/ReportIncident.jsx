import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet'
import { incidentsAPI } from '../../api/incidents'
import Card from '../../components/common/Card'
import Input from '../../components/common/Input'
import Button from '../../components/common/Button'
import Alert from '../../components/common/Alert'
import L from 'leaflet'
import { MapPin, Navigation } from 'lucide-react'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const INCIDENT_TYPES = [
  { value: 'flood', label: 'Flood', color: 'bg-blue-500' },
  { value: 'fire', label: 'Fire', color: 'bg-red-500' },
  { value: 'medical', label: 'Medical Emergency', color: 'bg-red-600' },
  { value: 'accident', label: 'Accident', color: 'bg-orange-500' },
  { value: 'other', label: 'Other', color: 'bg-gray-500' },
]

const PRIORITIES = [
  { value: 'critical', label: 'Critical', description: 'Immediate threat to life' },
  { value: 'high', label: 'High', description: 'Urgent but stable' },
  { value: 'medium', label: 'Medium', description: 'Needs attention soon' },
  { value: 'low', label: 'Low', description: 'Non-urgent situation' },
]

function LocationPicker({ position, setPosition }) {
  useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng])
    },
  })

  return position ? <Marker position={position} /> : null
}

export default function ReportIncident() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    type: 'flood',
    description: '',
    priority: 'medium',
  })
  const [position, setPosition] = useState(null)
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: (data) => incidentsAPI.create(data),
    onSuccess: (response) => {
      const incidentId = response.data.incident.id
      navigate(`/incidents/${incidentId}`)
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Failed to submit incident')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')

    if (!position) {
      setError('Please select a location on the map')
      return
    }

    if (formData.description.length < 10) {
      setError('Please provide a more detailed description')
      return
    }

    mutation.mutate({
      ...formData,
      latitude: position[0],
      longitude: position[1],
    })
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Report an Emergency</h1>

      {error && (
        <Alert type="error" className="mb-6">
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Card className="mb-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Incident Type</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {INCIDENT_TYPES.map((type) => (
              <label
                key={type.value}
                className={`
                  flex flex-col items-center p-3 border rounded-lg cursor-pointer transition-colors
                  ${formData.type === type.value
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:border-gray-600'
                  }
                `}
              >
                <input
                  type="radio"
                  name="type"
                  value={type.value}
                  checked={formData.type === type.value}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="sr-only"
                />
                <span className={`w-4 h-4 rounded-full ${type.color} mb-2`} />
                <span className="text-sm font-medium text-gray-900 dark:text-white">{type.label}</span>
              </label>
            ))}
          </div>
        </Card>

        <Card className="mb-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Priority Level</h3>
          <div className="grid md:grid-cols-2 gap-3">
            {PRIORITIES.map((priority) => (
              <label
                key={priority.value}
                className={`
                  flex items-start p-3 border rounded-lg cursor-pointer transition-colors
                  ${formData.priority === priority.value
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:border-gray-600'
                  }
                `}
              >
                <input
                  type="radio"
                  name="priority"
                  value={priority.value}
                  checked={formData.priority === priority.value}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  className="sr-only"
                />
                <div>
                  <span className="font-medium text-gray-900 dark:text-white">{priority.label}</span>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{priority.description}</p>
                </div>
              </label>
            ))}
          </div>
        </Card>

        <Card className="mb-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Description</h3>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Describe the emergency in detail (what happened, how many people are involved, any hazards...)"
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          />
        </Card>

        <Card className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900 dark:text-white">Location</h3>
            {position && (
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {position[0].toFixed(6)}, {position[1].toFixed(6)}
              </span>
            )}
          </div>
          <div className="h-80 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
            <MapContainer
              center={[26.9124, 75.7873]}
              zoom={13}
              className="h-full w-full"
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <LocationPicker position={position} setPosition={setPosition} />
            </MapContainer>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 flex items-center gap-1">
            <MapPin className="h-4 w-4" />
            Click on the map to set the incident location
          </p>
        </Card>

        <div className="flex justify-end gap-4">
          <Button variant="secondary" type="button" onClick={() => navigate(-1)}>
            Cancel
          </Button>
          <Button type="submit" loading={mutation.isPending}>
            <Navigation className="h-4 w-4 mr-2" />
            Submit Report
          </Button>
        </div>
      </form>
    </div>
  )
}
