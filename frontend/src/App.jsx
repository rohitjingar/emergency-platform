import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/layout/Layout'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import AffectedDashboard from './pages/affected/Dashboard'
import ReportIncident from './pages/affected/ReportIncident'
import MyIncidents from './pages/affected/MyIncidents'
import IncidentStatus from './pages/affected/IncidentStatus'
import VolunteerDashboard from './pages/volunteer/Dashboard'
import VolunteerRegister from './pages/volunteer/Register'
import PendingIncidents from './pages/volunteer/PendingIncidents'
import VolunteerMap from './pages/volunteer/Map'
import AdminDashboard from './pages/admin/Dashboard'
import ReviewQueue from './pages/admin/ReviewQueue'
import SystemHealth from './pages/admin/SystemHealth'
import Notifications from './pages/shared/Notifications'

function ProtectedRoute({ children, roles }) {
  const { user, isAuthenticated } = useAuth()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  if (roles && !roles.includes(user?.role)) {
    return <Navigate to="/" replace />
  }
  
  return children
}

function App() {
  const { isAuthenticated, user } = useAuth()
  
  const getDashboardRoute = () => {
    switch (user?.role) {
      case 'admin': return '/admin'
      case 'volunteer': return '/volunteer'
      default: return '/dashboard'
    }
  }

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to={getDashboardRoute()} /> : <Login />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to={getDashboardRoute()} /> : <Register />} />
      
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to={getDashboardRoute()} />} />
        
        <Route path="notifications" element={
          <ProtectedRoute><Notifications /></ProtectedRoute>
        } />
        
        {/* Affected User Routes */}
        <Route path="dashboard" element={
          <ProtectedRoute roles={['affected_user']}><AffectedDashboard /></ProtectedRoute>
        } />
        <Route path="report" element={
          <ProtectedRoute roles={['affected_user']}><ReportIncident /></ProtectedRoute>
        } />
        <Route path="my-incidents" element={
          <ProtectedRoute roles={['affected_user']}><MyIncidents /></ProtectedRoute>
        } />
        <Route path="incidents/:id" element={
          <ProtectedRoute roles={['affected_user']}><IncidentStatus /></ProtectedRoute>
        } />
        
        {/* Volunteer Routes */}
        <Route path="volunteer" element={
          <ProtectedRoute roles={['volunteer']}><VolunteerDashboard /></ProtectedRoute>
        } />
        <Route path="volunteer/register" element={
          <ProtectedRoute roles={['volunteer']}><VolunteerRegister /></ProtectedRoute>
        } />
        <Route path="volunteer/pending" element={
          <ProtectedRoute roles={['volunteer']}><PendingIncidents /></ProtectedRoute>
        } />
        <Route path="volunteer/map" element={
          <ProtectedRoute roles={['volunteer']}><VolunteerMap /></ProtectedRoute>
        } />
        
        {/* Admin Routes */}
        <Route path="admin" element={
          <ProtectedRoute roles={['admin']}><AdminDashboard /></ProtectedRoute>
        } />
        <Route path="admin/review" element={
          <ProtectedRoute roles={['admin']}><ReviewQueue /></ProtectedRoute>
        } />
        <Route path="admin/system" element={
          <ProtectedRoute roles={['admin']}><SystemHealth /></ProtectedRoute>
        } />
      </Route>
    </Routes>
  )
}

export default App
