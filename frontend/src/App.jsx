import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Sidebar from './components/Sidebar'
import Toast from './components/Toast'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import OrgHierarchy from './pages/OrgHierarchy'
import AdminApproval from './pages/AdminApproval'
import TaskDetail from './pages/TaskDetail'

function ProtectedLayout() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/organization" element={<OrgHierarchy />} />
          <Route path="/approvals" element={<AdminApproval />} />
          <Route path="/tasks/:id" element={<TaskDetail />} />
        </Routes>
      </div>
    </div>
  )
}

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><div className="spinner" /></div>
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <>
      <Toast />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/*" element={<ProtectedRoute><ProtectedLayout /></ProtectedRoute>} />
      </Routes>
    </>
  )
}
