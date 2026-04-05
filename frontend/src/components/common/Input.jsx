export default function Input({ label, error, required, ...props }) {
  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        className={`
          w-full px-3 py-2 border rounded-lg transition-colors
          bg-white dark:bg-gray-800
          text-gray-900 dark:text-white
          border-gray-300 dark:border-gray-600
          placeholder-gray-400 dark:placeholder-gray-500
          focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400
          focus:border-transparent
          ${error ? 'border-red-500 dark:border-red-400' : ''}
        `}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-red-500 dark:text-red-400">{error}</p>}
    </div>
  )
}
