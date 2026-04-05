export default function Card({ children, className = '' }) {
  return (
    <div className={`bg-white dark:bg-gray-900 rounded-xl shadow-md border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
      {children}
    </div>
  )
}
