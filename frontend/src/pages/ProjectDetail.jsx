import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { projectsAPI, tasksAPI, activityAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import KanbanBoard from '../components/KanbanBoard'
import AddMemberModal from '../components/AddMemberModal'
import CreateTaskModal from '../components/CreateTaskModal'
import ActivityFeed from '../components/ActivityFeed'

export default function ProjectDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [tasks, setTasks] = useState([])
  const [logs, setLogs] = useState([])
  const [myRole, setMyRole] = useState('member')
  const [tab, setTab] = useState('board')
  const [showAddMember, setShowAddMember] = useState(false)
  const [showCreateTask, setShowCreateTask] = useState(false)
  const wsRef = useRef(null)

  const fetchAll = async () => {
    try {
      const [p, t, a] = await Promise.all([
        projectsAPI.get(id),
        tasksAPI.list({ project_id: id }),
        activityAPI.get(id),
      ])
      setProject(p.data)
      setTasks(t.data)
      setLogs(a.data)
      const me = p.data.members.find(m => m.user.id === user?.id)
      if (me) setMyRole(me.role)
    } catch { toast.error('Failed to load project') }
  }

  // WebSocket real-time updates
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) return
    const wsBase = import.meta.env.VITE_WS_URL || (window.location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + window.location.host
    const ws = new WebSocket(`${wsBase}/ws/${id}?token=${token}`)
    wsRef.current = ws
    ws.onmessage = (e) => {
      const event = JSON.parse(e.data)
      if (['task_created', 'task_updated', 'task_deleted', 'member_added', 'member_removed'].includes(event.type)) {
        fetchAll()
        toast.info(`Real-time: ${event.type.replace('_', ' ')}`)
      }
    }
    const ping = setInterval(() => ws.readyState === WebSocket.OPEN && ws.send('ping'), 20000)
    return () => { ws.close(); clearInterval(ping) }
  }, [id])

  useEffect(() => { fetchAll() }, [id])

  const handleDelete = async () => {
    if (!window.confirm('Delete this project? This cannot be undone.')) return
    try { await projectsAPI.delete(id); toast.success('Project deleted'); navigate('/projects') }
    catch { toast.error('Failed to delete project') }
  }

  const handleRemoveMember = async (userId) => {
    try { await projectsAPI.removeMember(id, userId); toast.success('Member removed'); fetchAll() }
    catch (err) { toast.error(err.response?.data?.detail || 'Failed') }
  }

  if (!project) return <div className="page-content"><div className="spinner" /></div>

  const isAdmin = myRole === 'admin'

  return (
    <div className="page-content">
      {/* Header */}
      <div className="flex items-center justify-between mb-lg">
        <div>
          <div className="flex items-center gap-sm mb-sm">
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/projects')}>← Back</button>
            <span className={`badge badge-${myRole}`}>{myRole}</span>
          </div>
          <h1>{project.title}</h1>
          {project.description && <p className="text-muted text-sm" style={{ marginTop: 4 }}>{project.description}</p>}
        </div>
        <div className="flex gap-sm">
          {isAdmin && <button className="btn btn-primary btn-sm" onClick={() => setShowCreateTask(true)}>+ Task</button>}
          {isAdmin && <button className="btn btn-secondary btn-sm" onClick={() => setShowAddMember(true)}>👤 Add Member</button>}
          {isAdmin && <button className="btn btn-danger btn-sm" onClick={handleDelete}>🗑️</button>}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-sm mb-lg" style={{ borderBottom: '1px solid var(--border)', paddingBottom: 'var(--space-sm)' }}>
        {['board', 'members', 'activity'].map(t => (
          <button key={t} className={`btn btn-sm ${tab === t ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setTab(t)}>
            {t === 'board' ? '📋 Board' : t === 'members' ? '👥 Members' : '📜 Activity'}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === 'board' && <KanbanBoard tasks={tasks} isAdmin={isAdmin} />}

      {tab === 'members' && (
        <div className="card" style={{ maxWidth: 600 }}>
          <h3 className="mb-md">Team Members ({project.members.length})</h3>
          {project.members.map(m => (
            <div key={m.id} className="flex items-center justify-between" style={{ padding: 'var(--space-sm) 0', borderBottom: '1px solid var(--border)' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{m.user.name}</div>
                <div className="text-xs text-muted">{m.user.email}</div>
              </div>
              <div className="flex items-center gap-sm">
                <span className={`badge badge-${m.role}`}>{m.role}</span>
                {isAdmin && m.user.id !== user?.id && (
                  <button className="btn btn-danger btn-sm btn-icon" onClick={() => handleRemoveMember(m.user.id)} title="Remove">✕</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'activity' && (
        <div className="card" style={{ maxWidth: 600 }}>
          <h3 className="mb-md">Activity Log</h3>
          <ActivityFeed logs={logs} />
        </div>
      )}

      {showAddMember && <AddMemberModal projectId={id} onClose={() => setShowAddMember(false)} onAdded={fetchAll} />}
      {showCreateTask && <CreateTaskModal projectId={id} members={project.members} onClose={() => setShowCreateTask(false)} onCreated={fetchAll} />}
    </div>
  )
}
