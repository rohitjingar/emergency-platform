import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useTheme } from '../../context/ThemeContext'
import { useQuery } from '@tanstack/react-query'
import { notificationsAPI } from '../../api/notifications'
import { Bell, LogOut, Menu, X, AlertTriangle, User, Shield, MapPin, Sun, Moon } from 'lucide-react'
import { useState } from 'react'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const { data: notifData } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsAPI.getMy(),
    refetchInterval: 10000,
  })

  const unreadCount = notifData?.data?.notifications?.filter(n => !n.is_read).length || 0

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const roleBasedLinks = {
    affected_user: [
      { label: 'Dashboard', path: '/dashboard' },
      { label: 'Report Incident', path: '/report' },
      { label: 'My Incidents', path: '/my-incidents' },
    ],
    volunteer: [
      { label: 'Dashboard', path: '/volunteer' },
      { label: 'Pending', path: '/volunteer/pending' },
      { label: 'Map', path: '/volunteer/map' },
    ],
    admin: [
      { label: 'Dashboard', path: '/admin' },
      { label: 'Review Queue', path: '/admin/review' },
      { label: 'System', path: '/admin/system' },
    ],
  }

  const links = roleBasedLinks[user?.role] || []

  const RoleIcon = {
    affected_user: User,
    volunteer: MapPin,
    admin: Shield,
  }[user?.role] || User

  return (
    <nav className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <span className="font-bold text-xl text-gray-900 dark:text-white">Emergency Platform</span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            {links.map(link => (
              <Link
                key={link.path}
                to={link.path}
                className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={toggleTheme}
              className="p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
            <Link
              to="/notifications"
              className="relative p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                  {unreadCount}
                </span>
              )}
            </Link>

            <div className="hidden md:flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-lg">
                <RoleIcon className="h-4 w-4 text-gray-600 dark:text-gray-300" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">{user?.role?.replace('_', ' ')}</span>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>

            <button
              className="md:hidden p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
              onClick={() => setMobileOpen(!mobileOpen)}
            >
              {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {mobileOpen && (
          <div className="md:hidden py-4 border-t border-gray-200 dark:border-gray-700">
            {links.map(link => (
              <Link
                key={link.path}
                to={link.path}
                className="block py-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onClick={() => setMobileOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <div className="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <RoleIcon className="h-4 w-4 text-gray-600 dark:text-gray-300" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">{user?.role?.replace('_', ' ')}</span>
              </div>
              <button onClick={handleLogout} className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300">
                Logout
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
