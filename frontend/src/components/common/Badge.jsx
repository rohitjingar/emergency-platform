const severityColors = {
  Critical: 'bg-red-100 text-red-800 border-red-200',
  High: 'bg-orange-100 text-orange-800 border-orange-200',
  Medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  Low: 'bg-green-100 text-green-800 border-green-200',
}

const severityDot = {
  Critical: 'bg-red-500',
  High: 'bg-orange-500',
  Medium: 'bg-yellow-500',
  Low: 'bg-green-500',
}

export function SeverityBadge({ severity }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${severityColors[severity] || 'bg-gray-100 text-gray-800'}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${severityDot[severity] || 'bg-gray-500'}`} />
      {severity}
    </span>
  )
}

export function StatusBadge({ status }) {
  const statusStyles = {
    open: 'bg-blue-100 text-blue-800',
    triaging: 'bg-purple-100 text-purple-800',
    searching: 'bg-yellow-100 text-yellow-800',
    pending_assignment: 'bg-orange-100 text-orange-800',
    assigned: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  }

  return (
    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[status] || 'bg-gray-100 text-gray-800'}`}>
      {status?.replace(/_/g, ' ')}
    </span>
  )
}
