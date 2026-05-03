import React, { useState, useEffect } from 'react'
import { orgAPI, authAPI } from '../services/api'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

export default function AdminApproval() {
  const [pending, setPending] = useState([])
  const [loading, setLoading] = useState(true)
  const [processingId, setProcessingId] = useState(null)
  const { user } = useAuth()
  const isAdmin = user?.role === 'ceo' || user?.role === 'head'

  useEffect(() => {
    if (isAdmin) fetchPending()
  }, [])

  const fetchPending = async () => {
    try {
      const r = await orgAPI.members()
      setPending(r.data.filter(u => u.status === 'pending'))
    } catch (err) {
      toast.error('Failed to load pending users')
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (id, status) => {
    setProcessingId(id)
    try {
      await authAPI.approve(id, status)
      toast.success(`User successfully ${status}`)
      fetchPending()
    } catch (err) {
      const msg = err.response?.data?.detail || 'Action failed'
      toast.error(msg)
    } finally {
      setProcessingId(null)
    }
  }

  if (!isAdmin) return <div className="p-lg">Access Denied</div>

  return (
    <div className="p-lg page-fade">
      <div className="flex justify-between items-center mb-lg">
        <h1>Member Approvals</h1>
        <button className="btn btn-secondary btn-sm" onClick={fetchPending} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh List'}
        </button>
      </div>

      {loading ? (
        <div className="glass p-lg text-center text-muted">Scanning hierarchy...</div>
      ) : pending.length === 0 ? (
        <div className="glass p-lg text-center text-muted">No pending approvals found.</div>
      ) : (
        <div className="grid gap-md">
          {pending.map(u => (
            <div key={u.id} className="glass p-md flex justify-between items-center animate-slide-in">
              <div>
                <div className="text-bold">{u.full_name || u.name}</div>
                <div className="text-muted text-sm">{u.email} • <span className="text-accent">{u.role}</span></div>
              </div>
              <div className="flex gap-sm">
                <button 
                  className="btn btn-primary btn-sm" 
                  onClick={() => handleAction(u.id, 'approved')}
                  disabled={processingId === u.id}
                >
                  {processingId === u.id ? '...' : 'Approve'}
                </button>
                <button 
                  className="btn btn-secondary btn-sm" 
                  onClick={() => handleAction(u.id, 'rejected')}
                  disabled={processingId === u.id}
                >
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
