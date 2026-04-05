import { Link } from 'react-router-dom'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { useAuth } from '../../context/AuthContext'
import { AlertTriangle, Plus, List, Clock } from 'lucide-react'

export default function AffectedDashboard() {
  const { user } = useAuth()

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Welcome, {user?.email}</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Report emergencies and track their status</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <Card className="text-center hover:shadow-md transition-shadow">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-red-100 rounded-full mb-4">
            <AlertTriangle className="h-6 w-6 text-red-600" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Report Emergency</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Submit a new incident report</p>
          <Link to="/report">
            <Button variant="primary" className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              New Report
            </Button>
          </Link>
        </Card>

        <Card className="text-center hover:shadow-md transition-shadow">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mb-4">
            <List className="h-6 w-6 text-blue-600" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">My Incidents</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">View your reported incidents</p>
          <Link to="/my-incidents">
            <Button variant="secondary" className="w-full">
              View All
            </Button>
          </Link>
        </Card>

        <Card className="text-center hover:shadow-md transition-shadow">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-yellow-100 rounded-full mb-4">
            <Clock className="h-6 w-6 text-yellow-600" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Quick Help</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Call emergency services</p>
          <a href="tel:911">
            <Button variant="danger" className="w-full">
              Call 911
            </Button>
          </a>
        </Card>
      </div>

      <Card title="How It Works">
        <div className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center font-bold text-primary-600">
              1
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">Submit Incident</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">Report the emergency with location and description</p>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center font-bold text-primary-600">
              2
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">AI Triage</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">Our AI assesses severity and finds the right responders</p>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center font-bold text-primary-600">
              3
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">Volunteer Assigned</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">Nearest qualified volunteer is notified and dispatched</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}
