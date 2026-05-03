import { useState, useEffect } from 'react'
import { projectsAPI } from '../services/api'
import { useToast } from '../context/ToastContext'
import ProjectCard from '../components/ProjectCard'

export default function Projects() {
  const [projects, setProjects] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ title: '', description: '' })
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const fetchProjects = () => projectsAPI.list().then(r => setProjects(r.data)).catch(() => {})

  useEffect(() => { fetchProjects() }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await projectsAPI.create(form)
      toast.success('Project created!')
      setShowModal(false)
      setForm({ title: '', description: '' })
      fetchProjects()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create project')
    } finally { setLoading(false) }
  }

  return (
    <div className="page-content">
      <div className="flex items-center justify-between mb-lg">
        <div>
          <h1>Projects</h1>
          <p className="text-muted text-sm">{projects.length} project{projects.length !== 1 ? 's' : ''}</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ New Project</button>
      </div>

      {projects.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 'var(--space-2xl)' }}>
          <div style={{ fontSize: '4rem', marginBottom: 'var(--space-md)' }}>🏗️</div>
          <h3 className="mb-sm">No projects yet</h3>
          <p className="text-muted mb-md">Create your first project to get started</p>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>Create Project</button>
        </div>
      ) : (
        <div className="grid-3">
          {projects.map(p => <ProjectCard key={p.id} project={p} />)}
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>New Project</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreate} className="auth-form">
              <div className="form-group">
                <label className="form-label">Project Title *</label>
                <input className="form-input" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="e.g. Website Redesign" required />
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea className="form-textarea" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} placeholder="What is this project about?" />
              </div>
              <button className="btn btn-primary full-width" type="submit" disabled={loading}>
                {loading ? <span className="spinner" /> : '🚀 Create Project'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
