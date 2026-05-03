import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { tasksAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import dayjs from 'dayjs'

const priorityClass = { low: 'badge-low', medium: 'badge-medium', high: 'badge-high' }

export default function TaskDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [task, setTask] = useState(null)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(false)

  const fetchTask = async () => {
    try { const r = await tasksAPI.get(id); setTask(r.data); setForm(r.data) }
    catch { toast.error('Failed to load task') }
  }

  useEffect(() => { fetchTask() }, [id])

  const canEdit = user?.role !== 'employee'
  const isEmployee = user?.role === 'employee'

  const handleUpdate = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      let payload
      if (isEmployee) {
        payload = { status: form.status }
      } else {
        payload = {
          status: form.status,
          title: form.title,
          description: form.description,
          priority: form.priority,
          due_date: form.due_date,
          assigned_to: form.assigned_to,
          result: form.result
        }
      }
      // Allow employees to also update the result when finishing tasks
      if (isEmployee) payload.result = form.result
      await tasksAPI.update(id, payload)
      toast.success('Task updated')
      setEditing(false)
      fetchTask()
    } catch (err) { toast.error(err.response?.data?.detail || 'Update failed') }
    finally { setLoading(false) }
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete this task?')) return
    try { await tasksAPI.delete(id); toast.success('Task deleted'); navigate(-1) }
    catch (err) { toast.error(err.response?.data?.detail || 'Delete failed') }
  }

  if (!task) return <div className="page-content"><div className="spinner" /></div>

  return (
    <div className="page-content" style={{ maxWidth: 700, margin: '0 auto' }}>
      <button className="btn btn-ghost btn-sm mb-md" onClick={() => navigate(-1)}>← Back</button>

      <div className="card">
        <div className="flex items-center justify-between mb-lg">
          <div className="flex gap-sm">
            <span className={`badge ${priorityClass[task.priority]}`}>{task.priority}</span>
            <span className={`badge ${task.status === 'done' ? 'badge-done' : task.status === 'doing' ? 'badge-progress' : 'badge-todo'}`}>
              {task.status?.toUpperCase()}
            </span>
          </div>
          <div className="flex gap-sm">
            {!editing && <button className="btn btn-secondary btn-sm" onClick={() => setEditing(true)}>✏️ {isEmployee ? 'Update Status' : 'Edit'}</button>}
            {canEdit && <button className="btn btn-danger btn-sm" onClick={handleDelete}>🗑️ Delete</button>}
          </div>
        </div>

        {editing ? (
          <form onSubmit={handleUpdate} className="auth-form">
            {!isEmployee && (
              <>
                <div className="form-group">
                  <label className="form-label">Title</label>
                  <input className="form-input" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea className="form-textarea" value={form.description || ''} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
                </div>
              </>
            )}
            
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Status</label>
                <select className="form-select" value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}>
                  <option value="todo">To Do</option>
                  <option value="doing">In Progress</option>
                  <option value="done">Completed</option>
                </select>
              </div>
              {!isEmployee && (
                <div className="form-group">
                  <label className="form-label">Priority</label>
                  <select className="form-select" value={form.priority} onChange={e => setForm(f => ({ ...f, priority: e.target.value }))}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              )}
            </div>
            
            {!isEmployee && (
              <div className="form-group">
                <label className="form-label">Due Date</label>
                <input className="form-input" type="date" value={form.due_date ? dayjs(form.due_date).format('YYYY-MM-DD') : ''} onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))} />
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Task Result / Completion Notes</label>
              <textarea 
                className="form-textarea" 
                placeholder="Describe the outcome or attach results..." 
                value={form.result || ''} 
                onChange={e => setForm(f => ({ ...f, result: e.target.value }))} 
              />
            </div>

            <div className="flex gap-sm">
              <button className="btn btn-primary" type="submit" disabled={loading}>{loading ? <span className="spinner" /> : 'Save Changes'}</button>
              <button className="btn btn-ghost" type="button" onClick={() => setEditing(false)}>Cancel</button>
            </div>
          </form>
        ) : (
          <div>
            <h2 style={{ marginBottom: 'var(--space-md)' }}>{task.title}</h2>
            {task.description && <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-lg)', lineHeight: 1.7 }}>{task.description}</p>}
            
            {task.result && (
              <div className="glass p-md mb-lg" style={{ borderLeft: '4px solid var(--success)' }}>
                <h4 className="text-xs uppercase tracking-wider text-muted mb-xs">Result / Outcome</h4>
                <p style={{ color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{task.result}</p>
              </div>
            )}

            <div className="divider" />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
              <div><span className="text-xs text-muted">Assigned to</span><div style={{ fontWeight: 600 }}>{task.assignee?.name || 'Unassigned'}</div></div>
              <div><span className="text-xs text-muted">Created by</span><div style={{ fontWeight: 600 }}>{task.creator?.name}</div></div>
              <div><span className="text-xs text-muted">Due Date</span><div style={{ fontWeight: 600 }}>{task.due_date ? dayjs(task.due_date).format('MMM D, YYYY') : '—'}</div></div>
              <div><span className="text-xs text-muted">Created</span><div style={{ fontWeight: 600 }}>{dayjs(task.created_at).format('MMM D, YYYY')}</div></div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
