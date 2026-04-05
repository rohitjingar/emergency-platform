import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet'
import { volunteersAPI } from '../../api/volunteers'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import Spinner from '../../components/common/Spinner'
import Alert from '../../components/common/Alert'
import L from 'leaflet'
import { MapPin, Navigation, UserPlus } from 'lucide-react'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

function LocationMarker({ position, setPosition }) {
  useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng])
    },
  })

  return position ? (
    <Marker position={position}>
      <Popup>Your location</Popup>
    </Marker>
  ) : null
}

export default function VolunteerMap() {
  const queryClient = useQueryClient()
  const [position, setPosition] = useState(null)
  const [selectedStatus, setSelectedStatus] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const { data: profileData, isLoading, error: profileError } = useQuery({
    queryKey: ['volunteer-profile'],
    queryFn: () => volunteersAPI.getProfile(),
    retry: false,
  })

  const hasProfile = profileData && !profileError

  const locationMutation = useMutation({
    mutationFn: (data) => volunteersAPI.updateLocation(data),
    onSuccess: () => {
      setSuccess('Location updated successfully!')
      queryClient.invalidateQueries(['volunteer-profile'])
      setTimeout(() => setSuccess(''), 3000)
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Failed to update location')
    },
  })

  const statusMutation = useMutation({
    mutationFn: (data) => volunteersAPI.updateStatus(data),
    onSuccess: () => {
      setSuccess(`Status changed to ${selectedStatus}`)
      queryClient.invalidateQueries(['volunteer-profile'])
      setTimeout(() => setSuccess(''), 3000)
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Failed to update status')
    },
  })

  const handleSaveLocation = () => {
    if (!position) {
      setError('Please select a location on the map first')
      return
    }
    setError('')
    locationMutation.mutate({
      latitude: position[0],
      longitude: position[1],
    })
  }

  const handleStatusChange = (newStatus) => {
    setSelectedStatus(newStatus)
    statusMutation.mutate({ status: newStatus })
  }

  const handleGetCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setPosition([pos.coords.latitude, pos.coords.longitude])
        },
        (err) => {
          setError('Could not get your location. Please select on the map.')
        }
      )
    } else {
      setError('Geolocation is not supported by your browser')
    }
  }

  if (isLoading) {
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
              You need to register your volunteer profile before you can set your location and availability.
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

  const currentStatus = profileData?.data?.availability_status || 'offline'
  const currentLocation = profileData?.data?.location

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Volunteer Map</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Update your location and availability status</p>
        </div>
        <div className="text-sm">
          <span className="text-gray-500 dark:text-gray-400">Current Status: </span>
          <span className={`
            px-2 py-1 rounded-full text-sm font-medium
            ${currentStatus === 'available' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}
          `}>
            {currentStatus}
          </span>
        </div>
      </div>

      {error && (
        <Alert type="error" className="mb-4" onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert type="success" className="mb-4" onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card title="Select Your Location" className="h-full">
            <div className="h-96 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 mb-4">
              <MapContainer
                center={currentLocation ? [currentLocation.x, currentLocation.y] : [26.9124, 75.7873]}
                zoom={13}
                className="h-full w-full"
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <LocationMarker position={position} setPosition={setPosition} />
              </MapContainer>
            </div>
            <div className="flex gap-3">
              <Button onClick={handleGetCurrentLocation}>
                <Navigation className="h-4 w-4 mr-2" />
                Use My Location
              </Button>
              <Button 
                variant="outline" 
                onClick={handleSaveLocation} 
                loading={locationMutation.isPending}
              >
                Save Location
              </Button>
            </div>
            {position && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                Selected: {position[0].toFixed(6)}, {position[1].toFixed(6)}
              </p>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Availability Status">
            <div className="space-y-3">
              {[
                { value: 'available', label: 'Available', color: 'bg-green-500', description: 'Receive incident alerts' },
                { value: 'busy', label: 'Busy', color: 'bg-yellow-500', description: 'Temporarily unavailable' },
                { value: 'offline', label: 'Offline', color: 'bg-gray-400', description: 'No alerts' },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => handleStatusChange(option.value)}
                  className={`
                    w-full flex items-center gap-3 p-4 border rounded-lg transition-colors
                    ${currentStatus === option.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:border-gray-600'
                    }
                  `}
                  disabled={statusMutation.isPending}
                >
                  <div className={`w-4 h-4 rounded-full ${option.color}`} />
                  <div className="text-left">
                    <div className="font-medium text-gray-900 dark:text-white">{option.label}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">{option.description}</div>
                  </div>
                </button>
              ))}
            </div>
          </Card>

          <Card>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Your Profile</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Skills:</span>
                <span className="font-medium">{profileData.data?.skills?.join(', ') || 'Not set'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Radius:</span>
                <span className="font-medium">{profileData.data?.radius_km || 10} km</span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Link to="/volunteer/register">
                <Button variant="ghost" size="sm" className="w-full">
                  Edit Profile
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
