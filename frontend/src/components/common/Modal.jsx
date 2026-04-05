import { X } from 'lucide-react'
import Button from './Button'

export default function Modal({ isOpen, onClose, title, children, footer }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} />
        
        <div className="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6 transform transition-all">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X size={20} />
            </button>
          </div>
          
          <div className="mb-6">{children}</div>
          
          {footer && (
            <div className="flex justify-end gap-3">{footer}</div>
          )}
        </div>
      </div>
    </div>
  )
}
