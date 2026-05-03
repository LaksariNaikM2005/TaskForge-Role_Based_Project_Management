import { useState } from 'react'
import { projectsAPI } from '../services/api'
import { useToast } from '../context/ToastContext'

export default function AddMemberModal({ projectId, onClose, onAdded }) {
  const [email, setEmail] = useState('')
  const [role, setRole] = useState('member')
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await projectsAPI.addMember(projectId, { email, role })
      toast.success(`${email} added as ${role}`)
      onAdded()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add member')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Add Member</h3>
          <button className="btn btn-ghost btn-icon" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input className="form-input" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="member@email.com" required />
          </div>
          <div className="form-group">
            <label className="form-label">Role</label>
            <select className="form-select" value={role} onChange={e => setRole(e.target.value)}>
              <option value="member">Member</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <button className="btn btn-primary full-width" type="submit" disabled={loading}>
            {loading ? <span className="spinner" /> : '➕ Add Member'}
          </button>
        </form>
      </div>
    </div>
  )
}
