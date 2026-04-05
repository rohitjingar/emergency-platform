import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import Spinner from '../../components/common/Spinner'
import Alert from '../../components/common/Alert'
import { useAuth } from '../../context/AuthContext'
import { volunteersAPI } from '../../api/volunteers'
import { UserPlus, MapPin, Bell, CheckCircle, Clock, AlertTriangle } from 'lucide-react'

export default function VolunteerDashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const { data: profileData, isLoading, error, refetch } = useQuery({
    queryKey: ['volunteer-profile'],
    queryFn: () => volunteersAPI.getProfile(),
    retry: false,
  })

  const hasProfile = profileData && !error

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Volunteer Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your response to emergencies</p>
      </div>

      {!hasProfile ? (
        <>
          <Alert type="warning" className="mb-6">
            <strong>Complete your profile to start responding!</strong>
            <p className="mt-1">Register your volunteer profile with your skills and location to receive incident alerts.</p>
          </Alert>

          <Card className="mb-6">
            <div className="text-center py-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
                <UserPlus className="h-8 w-8 text-primary-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Create Your Volunteer Profile</h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
                Set up your skills, response radius, and location to start receiving emergency alerts in your area.
              </p>
              <Link to="/volunteer/register">
                <Button size="lg">
                  <UserPlus className="h-5 w-5 mr-2" />
                  Register Now
                </Button>
              </Link>
            </div>
          </Card>

          <Card title="Getting Started">
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center font-bold">
                  <CheckCircle className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">1. Register Your Profile</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Set your skills and response radius</p>
                </div>
                <div className="ml-auto">
                  <Link to="/volunteer/register">
                    <Button size="sm">Start</Button>
                  </Link>
                </div>
              </div>
              <div className="flex gap-4 opacity-50">
                <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center font-bold text-gray-500 dark:text-gray-400">
                  2
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">Enable Location</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Allow location access so we can find you</p>
                </div>
              </div>
              <div className="flex gap-4 opacity-50">
                <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center font-bold text-gray-500 dark:text-gray-400">
                  3
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">Set Status to Available</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Toggle your availability to start receiving alerts</p>
                </div>
              </div>
            </div>
          </Card>
        </>
      ) : (
        <>
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <Card className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Profile Active</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 capitalize">{profileData.data?.availability_status || 'offline'}</p>
            </Card>

            <Card className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mb-3">
                <MapPin className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Location Set</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{profileData.data?.radius_km || 10}km radius</p>
            </Card>

            <Card className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 rounded-full mb-3">
                <Bell className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Ready to Help</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{profileData.data?.skills?.join(', ') || 'No skills set'}</p>
            </Card>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <Card className="hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-yellow-100 rounded-full">
                  <Clock className="h-6 w-6 text-yellow-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Pending Incidents</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">View and respond to assigned emergencies</p>
                  <Link to="/volunteer/pending">
                    <Button size="sm">View Pending</Button>
                  </Link>
                </div>
              </div>
            </Card>

            <Card className="hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full">
                  <MapPin className="h-6 w-6 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Update Location</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Keep your location current for better matching</p>
                  <Link to="/volunteer/map">
                    <Button variant="outline" size="sm">Open Map</Button>
                  </Link>
                </div>
              </div>
            </Card>
          </div>

          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white">Quick Actions</h3>
              <Link to="/volunteer/register">
                <Button variant="ghost" size="sm">Edit Profile</Button>
              </Link>
            </div>
            <div className="space-y-3">
              {profileData.data?.availability_status !== 'available' && (
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="h-5 w-5 text-yellow-600" />
                    <div>
                      <p className="font-medium text-yellow-900">You are not available</p>
                      <p className="text-sm text-yellow-700">Set your status to "Available" to receive alerts</p>
                    </div>
                    <Link to="/volunteer/map" className="ml-auto">
                      <Button size="sm" variant="success">Go Available</Button>
                    </Link>
                  </div>
                </div>
              )}
              <div className="flex gap-4">
                <div className="flex-1 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Skills</p>
                  <p className="font-medium text-gray-900 dark:text-white">{profileData.data?.skills?.join(', ') || 'Not set'}</p>
                </div>
                <div className="flex-1 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Response Radius</p>
                  <p className="font-medium text-gray-900 dark:text-white">{profileData.data?.radius_km || 10} km</p>
                </div>
              </div>
            </div>
          </Card>
        </>
      )}
    </div>
  )
}
