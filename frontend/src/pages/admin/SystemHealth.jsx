import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { systemAPI } from '../../api/system'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import Spinner from '../../components/common/Spinner'
import Alert from '../../components/common/Alert'
import { CheckCircle, XCircle, RefreshCw, Database, Zap, Clock } from 'lucide-react'

export default function SystemHealth() {
  const queryClient = useQueryClient()

  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['system-health'],
    queryFn: () => systemAPI.health(),
    refetchInterval: 5000,
  })

  const { data: circuitData, isLoading: circuitLoading } = useQuery({
    queryKey: ['circuit-breaker'],
    queryFn: () => systemAPI.circuitBreaker(),
  })

  const { data: queuesData, isLoading: queuesLoading } = useQuery({
    queryKey: ['queues'],
    queryFn: () => systemAPI.queues(),
  })

  const resetMutation = useMutation({
    mutationFn: () => systemAPI.resetCircuit(),
    onSuccess: () => {
      queryClient.invalidateQueries(['circuit-breaker'])
      queryClient.invalidateQueries(['system-health'])
    },
  })

  const health = healthData?.data
  const circuit = circuitData?.data
  const queues = queuesData?.data

  if (healthLoading || circuitLoading || queuesLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  const services = [
    { name: 'API Server', status: health?.api },
    { name: 'PostgreSQL + PostGIS', status: health?.postgres },
    { name: 'Redis Queue', status: health?.redis },
    { name: 'Circuit Breaker', status: health?.circuit_breaker },
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Health</h1>
          <p className="text-gray-600 mt-1">Monitor platform infrastructure</p>
        </div>
        <Button onClick={() => queryClient.invalidateQueries()} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Card title="Overall Status" className="mb-6">
        <div className="flex items-center gap-4">
          <div className={`
            w-16 h-16 rounded-full flex items-center justify-center
            ${health?.overall === 'ok' ? 'bg-green-100' : 'bg-red-100'}
          `}>
            {health?.overall === 'ok' ? (
              <CheckCircle className="h-8 w-8 text-green-600" />
            ) : (
              <XCircle className="h-8 w-8 text-red-600" />
            )}
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900 capitalize">{health?.overall || 'unknown'}</p>
            <p className="text-gray-600">
              {health?.overall === 'ok' ? 'All systems operational' : 'Some issues detected'}
            </p>
          </div>
        </div>
        {health?.issues?.length > 0 && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="font-medium text-red-900 mb-2">Issues detected:</p>
            <ul className="list-disc list-inside text-red-800">
              {health.issues.map((issue, i) => (
                <li key={i}>{issue}</li>
              ))}
            </ul>
          </div>
        )}
      </Card>

      <Card title="Services" className="mb-6">
        <div className="space-y-3">
          {services.map((service) => (
            <div key={service.name} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`
                  w-3 h-3 rounded-full
                  ${service.status === 'ok' ? 'bg-green-500' : 'bg-red-500'}
                `} />
                <span className="font-medium text-gray-900">{service.name}</span>
              </div>
              <span className={`
                px-3 py-1 rounded-full text-sm font-medium
                ${service.status === 'ok' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}
              `}>
                {service.status || 'unknown'}
              </span>
            </div>
          ))}
        </div>
      </Card>

      <div className="grid md:grid-cols-2 gap-6">
        <Card title="Circuit Breaker">
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <Zap className="h-5 w-5 text-yellow-600" />
                <span className="font-medium">State</span>
              </div>
              <span className={`
                px-3 py-1 rounded-full text-sm font-medium
                ${circuit?.state === 'closed' ? 'bg-green-100 text-green-800' :
                  circuit?.state === 'open' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'}
              `}>
                {circuit?.state || 'unknown'}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Failures</p>
                <p className="text-xl font-bold text-gray-900">
                  {circuit?.failures || 0}/{circuit?.threshold || 5}
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Last Failure</p>
                <p className="text-sm font-medium text-gray-900">
                  {circuit?.last_failure ? new Date(circuit.last_failure).toLocaleTimeString() : 'Never'}
                </p>
              </div>
            </div>
            <Button
              onClick={() => resetMutation.mutate()}
              loading={resetMutation.isPending}
              className="w-full"
            >
              Reset Circuit Breaker
            </Button>
          </div>
        </Card>

        <Card title="Queue Status">
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
              <Database className="h-5 w-5 text-blue-600" />
              <div className="flex-1">
                <p className="font-medium text-gray-900">Incidents Queue</p>
                <p className="text-sm text-gray-500">{queues?.incidents_queue?.waiting || 0} waiting</p>
              </div>
              <span className="text-sm text-gray-500">
                {queues?.incidents_queue?.failed || 0} failed
              </span>
            </div>
            <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
              <Clock className="h-5 w-5 text-green-600" />
              <div className="flex-1">
                <p className="font-medium text-gray-900">Assignment Queue</p>
                <p className="text-sm text-gray-500">{queues?.assignment_queue?.waiting || 0} waiting</p>
              </div>
              <span className="text-sm text-gray-500">
                {queues?.assignment_queue?.failed || 0} failed
              </span>
            </div>
            <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
              <Clock className="h-5 w-5 text-yellow-600" />
              <div className="flex-1">
                <p className="font-medium text-gray-900">Scheduler Queue</p>
                <p className="text-sm text-gray-500">{queues?.scheduler_queue?.waiting || 0} waiting</p>
              </div>
              <span className="text-sm text-gray-500">
                {queues?.scheduler_queue?.failed || 0} failed
              </span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
