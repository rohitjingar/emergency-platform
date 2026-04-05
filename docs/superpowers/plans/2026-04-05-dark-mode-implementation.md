# Dark Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add dark mode support to Emergency Platform with system preference detection and localStorage persistence.

**Architecture:** Use React context for theme state, Tailwind dark mode class strategy, localStorage for persistence, system preference detection for initial theme.

**Tech Stack:** React Context, Tailwind CSS, localStorage, prefers-color-scheme

---

## File Structure

**Create:**
- `frontend/src/context/ThemeContext.jsx` - Theme state management

**Modify:**
- `frontend/tailwind.config.js` - Enable darkMode
- `frontend/src/main.jsx` - Wrap with ThemeProvider
- `frontend/src/components/layout/Navbar.jsx` - Add toggle button, dark styles
- `frontend/src/components/layout/Layout.jsx` - Dark background
- `frontend/src/pages/auth/Login.jsx` - Dark styles
- `frontend/src/pages/auth/Register.jsx` - Dark styles
- `frontend/src/components/common/Card.jsx` - Dark styles
- `frontend/src/components/common/Input.jsx` - Dark styles
- `frontend/src/components/common/Button.jsx` - Dark styles
- `frontend/src/components/common/Alert.jsx` - Dark styles
- `frontend/src/pages/affected/Dashboard.jsx` - Dark styles
- `frontend/src/pages/affected/ReportIncident.jsx` - Dark styles
- `frontend/src/pages/affected/MyIncidents.jsx` - Dark styles
- `frontend/src/pages/volunteer/Dashboard.jsx` - Dark styles
- `frontend/src/pages/volunteer/Map.jsx` - Dark styles
- `frontend/src/pages/volunteer/PendingIncidents.jsx` - Dark styles
- `frontend/src/pages/admin/Dashboard.jsx` - Dark styles
- `frontend/src/pages/admin/ReviewQueue.jsx` - Dark styles
- `frontend/src/pages/admin/SystemHealth.jsx` - Dark styles

---

## Task 1: Create ThemeContext

**Files:**
- Create: `frontend/src/context/ThemeContext.jsx`

- [ ] **Step 1: Create ThemeContext with system detection and localStorage persistence**

```jsx
import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext(null)

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('theme')
      if (stored) return stored
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return 'light'
  })

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e) => {
      if (!localStorage.getItem('theme')) {
        setTheme(e.matches ? 'dark' : 'light')
      }
    }
    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/context/ThemeContext.jsx
git commit -m "feat: add ThemeContext for dark mode support"
```

---

## Task 2: Configure Tailwind

**Files:**
- Modify: `frontend/tailwind.config.js`

- [ ] **Step 1: Enable dark mode class strategy**

```js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        severity: {
          critical: '#dc2626',
          high: '#f97316',
          medium: '#eab308',
          low: '#22c55e',
        }
      }
    },
  },
  plugins: [],
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/tailwind.config.js
git commit -m "feat: enable Tailwind dark mode class strategy"
```

---

## Task 3: Update main.jsx

**Files:**
- Modify: `frontend/src/main.jsx`

- [ ] **Step 1: Wrap app with ThemeProvider**

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ThemeProvider>
          <AuthProvider>
            <App />
          </AuthProvider>
        </ThemeProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/main.jsx
git commit -m "feat: add ThemeProvider wrapper"
```

---

## Task 4: Update Navbar with Toggle Button

**Files:**
- Modify: `frontend/src/components/layout/Navbar.jsx`

- [ ] **Step 1: Add theme toggle button and dark styles**

```jsx
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
                <RoleIcon className="h-4 w-4 text-gray-600 dark:text-gray-400" />
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
                <RoleIcon className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">{user?.role?.replace('_', ' ')}</span>
              </div>
              <button onClick={handleLogout} className="text-red-600 hover:text-red-700 dark:text-red-400">
                Logout
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/layout/Navbar.jsx
git commit -m "feat: add dark mode toggle button to navbar"
```

---

## Task 5: Update Layout

**Files:**
- Modify: `frontend/src/components/layout/Layout.jsx`

- [ ] **Step 1: Add dark background**

```jsx
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Navbar />
      <main className="container mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/layout/Layout.jsx
git commit -m "feat: add dark mode styles to Layout"
```

---

## Task 6: Update Auth Pages (Login & Register)

**Files:**
- Modify: `frontend/src/pages/auth/Login.jsx`
- Modify: `frontend/src/pages/auth/Register.jsx`

- [ ] **Step 1: Update Login page with dark styles**

```jsx
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Input from '../../components/common/Input'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import Alert from '../../components/common/Alert'
import { AlertTriangle } from 'lucide-react'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(formData.email, formData.password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center gap-2 mb-4">
            <AlertTriangle className="h-12 w-12 text-red-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Emergency Platform</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Sign in to your account</p>
        </div>

        <Card>
          {error && (
            <Alert type="error" className="mb-6">
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Input
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
            />

            <Input
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
            />

            <Button type="submit" loading={loading} className="w-full">
              Sign In
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium">
              Register here
            </Link>
          </p>
        </Card>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Update Register page with dark styles**

```jsx
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Input from '../../components/common/Input'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import Alert from '../../components/common/Alert'
import { AlertTriangle } from 'lucide-react'

const ROLES = [
  { value: 'affected_user', label: 'Report Emergencies', description: 'Submit incident reports' },
  { value: 'volunteer', label: 'Volunteer', description: 'Respond to emergencies' },
  { value: 'admin', label: 'Admin', description: 'Manage and review incidents' },
]

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    role: 'affected_user',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    setLoading(true)

    try {
      await register(formData.email, formData.password, formData.role)
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center gap-2 mb-4">
            <AlertTriangle className="h-12 w-12 text-red-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Emergency Platform</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Create your account</p>
        </div>

        <Card>
          {error && (
            <Alert type="error" className="mb-6">
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Input
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
            />

            <Input
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Min 6 characters"
              required
            />

            <Input
              label="Confirm Password"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm your password"
              required
            />

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                I want to...
              </label>
              <div className="space-y-2">
                {ROLES.map((role) => (
                  <label
                    key={role.value}
                    className={`
                      flex items-center p-3 border rounded-lg cursor-pointer transition-colors
                      ${formData.role === role.value
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }
                    `}
                  >
                    <input
                      type="radio"
                      name="role"
                      value={role.value}
                      checked={formData.role === role.value}
                      onChange={handleChange}
                      className="sr-only"
                    />
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">{role.label}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{role.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <Button type="submit" loading={loading} className="w-full">
              Create Account
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium">
              Sign in
            </Link>
          </p>
        </Card>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/auth/Login.jsx frontend/src/pages/auth/Register.jsx
git commit -m "feat: add dark mode styles to auth pages"
```

---

## Task 7: Update Common Components

**Files:**
- Modify: `frontend/src/components/common/Card.jsx`
- Modify: `frontend/src/components/common/Input.jsx`
- Modify: `frontend/src/components/common/Button.jsx`
- Modify: `frontend/src/components/common/Alert.jsx`

- [ ] **Step 1: Update Card component**

```jsx
export default function Card({ children, className = '' }) {
  return (
    <div className={`bg-white dark:bg-gray-900 rounded-xl shadow-md border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
      {children}
    </div>
  )
}
```

- [ ] **Step 2: Update Input component**

```jsx
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
```

- [ ] **Step 3: Update Button component**

```jsx
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
```

- [ ] **Step 4: Update Alert component**

```jsx
const types = {
  success: 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300 border-green-200 dark:border-green-800',
  error: 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800',
  warning: 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800',
  info: 'bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800',
}

export default function Alert({ children, type = 'info', className = '' }) {
  return (
    <div className={`p-4 rounded-lg border ${types[type]} ${className}`}>
      {children}
    </div>
  )
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/common/Card.jsx frontend/src/components/common/Input.jsx frontend/src/components/common/Button.jsx frontend/src/components/common/Alert.jsx
git commit -m "feat: add dark mode styles to common components"
```

---

## Task 8: Update Affected User Pages

**Files:**
- Modify: `frontend/src/pages/affected/Dashboard.jsx`
- Modify: `frontend/src/pages/affected/ReportIncident.jsx`
- Modify: `frontend/src/pages/affected/MyIncidents.jsx`
- Modify: `frontend/src/pages/affected/IncidentStatus.jsx`

- [ ] **Step 1: Update Dashboard with dark styles**

```jsx
// Key changes for dark mode:
// - bg-white → dark:bg-gray-900
// - text-gray-600 → dark:text-gray-400
// - text-gray-900 → dark:text-white
// - border-gray-200 → dark:border-gray-700
// - bg-gray-50 → dark:bg-gray-800

// Read each file first and apply similar pattern
```

- [ ] **Step 2: Read affected pages to understand their structure**

```bash
cat frontend/src/pages/affected/Dashboard.jsx
cat frontend/src/pages/affected/ReportIncident.jsx
cat frontend/src/pages/affected/MyIncidents.jsx
cat frontend/src/pages/affected/IncidentStatus.jsx
```

- [ ] **Step 3: Apply dark mode classes to each page**

Apply these patterns:
- Containers: `bg-white dark:bg-gray-900 rounded-lg`
- Text: `text-gray-900 dark:text-white` (headings), `text-gray-600 dark:text-gray-400` (body)
- Borders: `border-gray-200 dark:border-gray-700`
- Cards: `bg-gray-50 dark:bg-gray-800`
- Tables: `bg-white dark:bg-gray-900`, `thead:bg-gray-50 dark:bg-gray-800`

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/affected/
git commit -m "feat: add dark mode styles to affected user pages"
```

---

## Task 9: Update Volunteer Pages

**Files:**
- Modify: `frontend/src/pages/volunteer/Dashboard.jsx`
- Modify: `frontend/src/pages/volunteer/Map.jsx`
- Modify: `frontend/src/pages/volunteer/PendingIncidents.jsx`
- Modify: `frontend/src/pages/volunteer/Register.jsx`

- [ ] **Step 1: Read volunteer pages to understand their structure**

```bash
cat frontend/src/pages/volunteer/Dashboard.jsx
cat frontend/src/pages/volunteer/Map.jsx
cat frontend/src/pages/volunteer/PendingIncidents.jsx
cat frontend/src/pages/volunteer/Register.jsx
```

- [ ] **Step 2: Apply same dark mode patterns as affected pages**

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/volunteer/
git commit -m "feat: add dark mode styles to volunteer pages"
```

---

## Task 10: Update Admin Pages

**Files:**
- Modify: `frontend/src/pages/admin/Dashboard.jsx`
- Modify: `frontend/src/pages/admin/ReviewQueue.jsx`
- Modify: `frontend/src/pages/admin/SystemHealth.jsx`

- [ ] **Step 1: Read admin pages to understand their structure**

```bash
cat frontend/src/pages/admin/Dashboard.jsx
cat frontend/src/pages/admin/ReviewQueue.jsx
cat frontend/src/pages/admin/SystemHealth.jsx
```

- [ ] **Step 2: Apply same dark mode patterns**

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/admin/
git commit -m "feat: add dark mode styles to admin pages"
```

---

## Task 11: Update shared Notifications Page

**Files:**
- Modify: `frontend/src/pages/shared/Notifications.jsx`

- [ ] **Step 1: Apply dark mode styles**

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/shared/Notifications.jsx
git commit -m "feat: add dark mode styles to notifications page"
```

---

## Task 12: Verify and Test

- [ ] **Step 1: Run dev server**

```bash
cd frontend && npm run dev
```

- [ ] **Step 2: Test dark mode toggle**
- Visit http://localhost:3000
- Click the moon/sun icon in navbar
- Verify colors change appropriately
- Refresh page - preference should persist

- [ ] **Step 3: Test system preference detection**
- Open browser dev tools
- Toggle system dark mode preference
- Refresh page
- Theme should follow system preference (if no stored preference)

- [ ] **Step 4: Verify all pages render correctly in both modes**
