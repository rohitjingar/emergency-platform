import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { adminAPI } from '../../api/admin'
import { systemAPI } from '../../api/system'
import Card from '../../components/common/Card'
import Spinner from '../../components/common/Spinner'
import { Shield, AlertTriangle, CheckCircle, Clock, Database, Zap } from 'lucide-react'

export default function AdminDashboard() {
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => adminAPI.getStats(),
  })

  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['system-health'],
    queryFn: () => systemAPI.health(),
  })

  const stats = statsData?.data
  const health = healthData?.data

  if (statsLoading || healthLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  const systemCards = [
    { label: 'API', status: health?.api, ok: 'ok', degraded: 'degraded' },
    { label: 'PostgreSQL', status: health?.postgres, ok: 'ok', degraded: 'down' },
    { label: 'Redis', status: health?.redis, ok: 'ok', degraded: 'down' },
    { label: 'Circuit Breaker', status: health?.circuit_breaker, ok: 'ok', degraded: 'open' },
  ]

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600 mt-1">Monitor and manage the emergency platform</p>
      </div>

      <div className="grid md:grid-cols-4 gap-4 mb-8">
        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats?.total_incidents || 0}</p>
              <p className="text-sm text-gray-500">Total Incidents</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats?.needs_review || 0}</p>
              <p className="text-sm text-gray-500">Needs Review</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats?.approved || 0}</p>
              <p className="text-sm text-gray-500">Approved</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <Zap className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats?.override_rate_percent?.toFixed(1) || 0}%</p>
              <p className="text-sm text-gray-500">Override Rate</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <Card title="System Health">
          <div className="space-y-3">
            {systemCards.map((item) => (
              <div key={item.label} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-900">{item.label}</span>
                <span className={`
                  px-3 py-1 rounded-full text-sm font-medium
                  ${item.status === item.ok ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}
                `}>
                  {item.status || 'unknown'}
                </span>
              </div>
            ))}
          </div>
          {health?.issues?.length > 0 && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">
                Issues: {health.issues.join(', ')}
              </p>
            </div>
          )}
        </Card>

        <Card title="AI Performance">
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Avg Confidence</span>
                <span className="font-medium">{(stats?.avg_confidence || 0).toFixed(1)}%</span>
              </div>
              <div className="bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full"
                  style={{ width: `${(stats?.avg_confidence || 0)}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Review Rate</span>
                <span className="font-medium">{stats?.review_rate_percent?.toFixed(1) || 0}%</span>
              </div>
              <div className="bg-gray-200 rounded-full h-2">
                <div
                  className="bg-yellow-500 h-2 rounded-full"
                  style={{ width: `${stats?.review_rate_percent || 0}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Override Rate</span>
                <span className="font-medium">{stats?.override_rate_percent?.toFixed(1) || 0}%</span>
              </div>
              <div className="bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full"
                  style={{ width: `${stats?.override_rate_percent || 0}%` }}
                />
              </div>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Link to="/admin/review">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Review Queue</h3>
                <p className="text-sm text-gray-500">{stats?.needs_review || 0} pending</p>
              </div>
            </div>
          </Card>
        </Link>

        <Link to="/admin/system">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Database className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">System Status</h3>
                <p className="text-sm text-gray-500">View all services</p>
              </div>
            </div>
          </Card>
        </Link>

        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Shield className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Quick Actions</h3>
              <p className="text-sm text-gray-500">Admin tools</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
