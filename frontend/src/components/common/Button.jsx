import { forwardRef } from 'react'
import Spinner from './Spinner'

const Button = forwardRef(({ children, variant = 'primary', loading, className = '', ...props }, ref) => {
  const baseClasses = 'inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  
  const variants = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white focus:ring-primary-500 dark:bg-primary-700 dark:hover:bg-primary-600',
    secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-900 focus:ring-gray-500 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
    ghost: 'hover:bg-gray-100 text-gray-700 dark:hover:bg-gray-800 dark:text-gray-300',
  }

  return (
    <button
      ref={ref}
      className={`${baseClasses} ${variants[variant]} ${className}`}
      disabled={loading}
      {...props}
    >
      {loading && <Spinner className="mr-2 h-4 w-4" />}
      {children}
    </button>
  )
})

Button.displayName = 'Button'
export default Button
