import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminAPI } from '../../api/admin'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import Spinner from '../../components/common/Spinner'
import Alert from '../../components/common/Alert'
import Modal from '../../components/common/Modal'
import Input from '../../components/common/Input'
import { SeverityBadge } from '../../components/common/Badge'
import { CheckCircle, XCircle, Edit, AlertTriangle, TrendingUp } from 'lucide-react'

const SEVERITY_OPTIONS = ['Critical', 'High', 'Medium', 'Low']

export default function ReviewQueue() {
  const queryClient = useQueryClient()
  const [overrideModal, setOverrideModal] = useState(null)
  const [overrideData, setOverrideData] = useState({ new_severity: '', reason: '' })

  const { data, isLoading, error } = useQuery({
    queryKey: ['review-queue'],
    queryFn: () => adminAPI.getReviewQueue(),
    refetchInterval: 5000,
  })

  const approveMutation = useMutation({
    mutationFn: (id) => adminAPI.approveIncident(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['review-queue'])
      queryClient.invalidateQueries(['admin-stats'])
    },
  })

  const overrideMutation = useMutation({
    mutationFn: ({ id, data }) => adminAPI.overrideIncident(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['review-queue'])
      queryClient.invalidateQueries(['admin-stats'])
      setOverrideModal(null)
      setOverrideData({ new_severity: '', reason: '' })
    },
  })

  const queue = data?.data?.review_queue || []
  const threshold = data?.data?.threshold || 0.7

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Review Queue</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Incidents requiring human review (confidence &lt; {threshold * 100}%)</p>
        </div>
      </div>

      {error && (
        <Alert type="error" className="mb-6">
          Failed to load review queue
        </Alert>
      )}

      {queue.length === 0 ? (
        <Card className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">All caught up!</h3>
          <p className="text-gray-600 dark:text-gray-400">No incidents require review at this time.</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {queue.map((item) => (
            <Card key={item.incident_id} className="hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-semibold text-gray-900 dark:text-white">#{item.incident_id}</span>
                    <span className="capitalize text-gray-700 dark:text-gray-300">{item.type}</span>
                    <SeverityBadge severity={item.severity} />
                  </div>
                  
                  <p className="text-gray-600 dark:text-gray-400 mb-3">{item.description}</p>
                  
                  <div className="flex items-center gap-6 text-sm text-gray-500 dark:text-gray-400 mb-3">
                    <span className="flex items-center gap-1">
                      <TrendingUp className="h-4 w-4" />
                      Confidence: {(item.confidence * 100).toFixed(0)}%
                    </span>
                    <span className="flex items-center gap-1">
                      <AlertTriangle className="h-4 w-4" />
                      {item.action_impact}
                    </span>
                    <span className="flex items-center gap-1">
                      <XCircle className="h-4 w-4" />
                      Attempts: {item.assignment_attempts}
                    </span>
                  </div>

                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      <span className="font-medium">AI Reasoning:</span> {item.reasoning}
                    </p>
                  </div>
                </div>

                <div className="flex flex-col gap-2 ml-4">
                  <Button
                    variant="success"
                    onClick={() => approveMutation.mutate(item.incident_id)}
                    loading={approveMutation.isPending}
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Approve
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setOverrideModal(item.incident_id)
                      setOverrideData({ new_severity: item.severity, reason: '' })
                    }}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Override
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal
        isOpen={!!overrideModal}
        onClose={() => setOverrideModal(null)}
        title="Override Severity"
        footer={
          <>
            <Button variant="secondary" onClick={() => setOverrideModal(null)}>Cancel</Button>
            <Button
              onClick={() => overrideMutation.mutate({ id: overrideModal, data: overrideData })}
              loading={overrideMutation.isPending}
              disabled={!overrideData.new_severity || !overrideData.reason}
            >
              Confirm Override
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">New Severity</label>
            <div className="grid grid-cols-2 gap-2">
              {SEVERITY_OPTIONS.map((sev) => (
                <button
                  key={sev}
                  onClick={() => setOverrideData({ ...overrideData, new_severity: sev })}
                  className={`
                    p-3 border rounded-lg transition-colors
                    ${overrideData.new_severity === sev
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:border-gray-600'
                    }
                  `}
                >
                  {sev}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Reason for Override</label>
            <textarea
              value={overrideData.reason}
              onChange={(e) => setOverrideData({ ...overrideData, reason: e.target.value })}
              placeholder="Explain why you're overriding the AI decision..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </Modal>
    </div>
  )
}
