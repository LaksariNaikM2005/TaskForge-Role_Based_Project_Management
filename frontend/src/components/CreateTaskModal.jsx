import { useState, useEffect } from 'react'
import { tasksAPI, usersAPI, projectsAPI, mlAPI } from '../services/api'
import { useToast } from '../context/ToastContext'
import { useAuth } from '../context/AuthContext'

export default function CreateTaskModal({ members, onClose, onCreated, projectId }) {
  const { user } = useAuth()
  const { toast } = useToast()
  
  const [form, setForm] = useState({ 
    title: '', 
    description: '', 
    priority: 'medium', 
    due_date: '', 
    assigned_to: '',
    project_id: projectId || '',
    department: '',
    team: ''
  })
  
  const [loading, setLoading] = useState(false)
  const [orgStructure, setOrgStructure] = useState({ departments: [], teams: [] })
  const [projects, setProjects] = useState([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [orgRes, projRes] = await Promise.all([
          usersAPI.getOrgStructure(),
          projectsAPI.list()
        ])
        setOrgStructure(orgRes.data)
        setProjects(projRes.data)
      } catch (err) {
        console.error('Failed to load org structure or projects', err)
      }
    }
    fetchData()
  }, [])

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleAutoPredict = async () => {
    if (!form.title) {
      toast.error('Please enter a title first to predict priority')
      return
    }
    try {
      setLoading(true)
      const res = await mlAPI.predictPriority({
        title: form.title,
        description: form.description
      })
      if (res.data && res.data.priority) {
        set('priority', res.data.priority)
        toast.success(`Priority predicted as: ${res.data.priority.toUpperCase()}`)
      }
    } catch (err) {
      toast.error('Failed to predict priority')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const payload = { ...form }
      if (!payload.due_date) delete payload.due_date
      if (!payload.assigned_to) delete payload.assigned_to
      if (!payload.project_id) delete payload.project_id
      if (!payload.department) delete payload.department
      if (!payload.team) delete payload.team
      
      await tasksAPI.create(payload)
      toast.success('Task created successfully')
      onCreated()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create task')
    } finally {
      setLoading(false)
    }
  }

  const isCEO = user?.role === 'ceo'
  const isHead = user?.role === 'head'

  // Helper to find selected department's teams
  const selectedDept = orgStructure.departments.find(d => d.name === form.department)
  const availableTeams = isHead 
    ? (orgStructure.departments.find(d => d.name === user.department)?.teams || [])
    : (selectedDept?.teams || [])

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" style={{ maxWidth: 600 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Create New Task</h3>
          <button className="btn btn-ghost btn-icon" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">Task Title *</label>
            <input className="form-input" value={form.title} onChange={e => set('title', e.target.value)} placeholder="Enter task title" required />
          </div>
          
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="form-textarea" value={form.description} onChange={e => set('description', e.target.value)} placeholder="Describe the task details..." />
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Project (Optional)</label>
              <select className="form-select" value={form.project_id} onChange={e => set('project_id', e.target.value)}>
                <option value="">No Project</option>
                {projects.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Assignee</label>
              <select className="form-select" value={form.assigned_to} onChange={e => set('assigned_to', e.target.value)}>
                <option value="">Unassigned</option>
                {members.map(m => <option key={m.id} value={m.id}>{m.name} ({m.role})</option>)}
              </select>
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                Priority
                <button type="button" onClick={handleAutoPredict} className="btn btn-ghost btn-sm" style={{ padding: '2px 8px', fontSize: '0.8rem' }} disabled={loading}>
                  🪄 Auto-Predict
                </button>
              </label>
              <select className="form-select" value={form.priority} onChange={e => set('priority', e.target.value)}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Due Date</label>
              <input className="form-input" type="date" value={form.due_date} onChange={e => set('due_date', e.target.value)} />
            </div>
          </div>

          {isCEO && (
            <div className="form-group animate-slide-in">
              <label className="form-label">Assign to Department</label>
              <select className="form-select" value={form.department} onChange={e => {
                set('department', e.target.value)
                set('team', '') // Reset team when department changes
              }}>
                <option value="">No Department (Org-wide)</option>
                {orgStructure.departments.map(d => (
                  <option key={d.name} value={d.name}>{d.name} (Head: {d.head_name})</option>
                ))}
              </select>
              {form.department && (
                <div className="form-group mt-sm animate-fade-in">
                  <label className="form-label">Assign to Team (Optional)</label>
                  <select className="form-select" value={form.team} onChange={e => set('team', e.target.value)}>
                    <option value="">Whole Department</option>
                    {availableTeams.map(t => (
                      <option key={t.name} value={t.name}>{t.name} (Lead: {t.leader_name})</option>
                    ))}
                  </select>
                </div>
              )}
              <p className="text-xs text-muted mt-xs">Task will be visible to the selected level.</p>
            </div>
          )}

          {isHead && (
            <div className="form-group">
              <label className="form-label">Assign to Team</label>
              <select className="form-select" value={form.team} onChange={e => set('team', e.target.value)}>
                <option value="">Whole Department ({user.department})</option>
                {availableTeams.map(t => (
                  <option key={t.name} value={t.name}>{t.name} (Leader: {t.leader_name})</option>
                ))}
              </select>
              <p className="text-xs text-muted mt-xs">Task will be visible to the team leader and their members.</p>
            </div>
          )}

          <button className="btn btn-primary full-width mt-md" type="submit" disabled={loading}>
            {loading ? <span className="spinner" /> : '✅ Create Task'}
          </button>
        </form>
      </div>
    </div>
  )
}
