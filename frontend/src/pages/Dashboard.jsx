import { useState, useEffect } from 'react'
import { tasksAPI, orgAPI, usersAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import StatCard from '../components/StatCard'
import KanbanBoard from '../components/KanbanBoard'
import CreateTaskModal from '../components/CreateTaskModal'
import OrgStructureView from '../components/OrgStructureView'

export default function Dashboard() {
  const { user } = useAuth()
  const { toast } = useToast()
  const [tasks, setTasks] = useState([])
  const [members, setMembers] = useState([])
  const [orgStructure, setOrgStructure] = useState({ departments: [] })
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [activeTab, setActiveTab] = useState('board') // 'board' or 'org'

  const fetchData = async () => {
    try {
      const [tRes, mRes, oRes] = await Promise.all([
        tasksAPI.list(),
        orgAPI.members(),
        usersAPI.getOrgStructure()
      ])
      setTasks(tRes.data)
      setMembers(mRes.data)
      setOrgStructure(oRes.data)
    } catch (err) { 
      console.error('Dashboard load error:', err)
      toast.error('Failed to load dashboard') 
    }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchData() }, [])

  if (loading) return <div className="page-content"><div className="spinner" /></div>

  const stats = {
    total: tasks.length,
    todo: tasks.filter(t => t.status === 'todo').length,
    doing: tasks.filter(t => t.status === 'doing').length,
    done: tasks.filter(t => t.status === 'done').length,
  }

  const isManagement = user?.role !== 'employee'

  const dashboardTitle = user?.role === 'ceo' 
    ? 'Company Overview' 
    : user?.role === 'head' 
    ? `${user.department} Hub` 
    : user?.role === 'leader' 
    ? `${user.team} Space` 
    : 'My Workspace'

  return (
    <div className="page-content">
      <div className="flex justify-between items-start mb-lg">
        <div>
          <h1>{dashboardTitle}</h1>
          <div className="flex gap-sm items-center mt-xs">
            <span className="badge badge-primary">{user?.role?.toUpperCase()}</span>
            {user?.department && (
              <span className="text-sm text-muted">
                🏢 <strong>{user.department}</strong>
                {user.team && <span> / 👥 {user.team}</span>}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-sm">
          <div className="tab-group mr-sm">
            <button className={`btn btn-sm ${activeTab === 'board' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setActiveTab('board')}>📋 Tasks</button>
            <button className={`btn btn-sm ${activeTab === 'org' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setActiveTab('org')}>🏢 Directory</button>
          </div>
          {isManagement && (
            <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ New Task</button>
          )}
        </div>
      </div>

      <div className="grid grid-4 gap-md mb-lg">
        <StatCard title="Total Tasks" value={stats.total} icon="📊" color="var(--primary)" />
        <StatCard title="To Do" value={stats.todo} icon="📝" color="var(--accent)" />
        <StatCard title="In Progress" value={stats.doing} icon="⚡" color="var(--warning)" />
        <StatCard title="Completed" value={stats.done} icon="✅" color="var(--success)" />
      </div>

      {activeTab === 'board' ? (
        <div className="mb-lg animate-fade-in">
          <h2 className="mb-md">Task Board</h2>
          <KanbanBoard tasks={tasks} isAdmin={isManagement} onUpdate={fetchData} />
        </div>
      ) : (
        <div className="mb-lg animate-slide-up">
          <h2 className="mb-md">Organizational Hierarchy</h2>
          <OrgStructureView structure={orgStructure} />
        </div>
      )}

      {showCreate && (
        <CreateTaskModal 
          onClose={() => setShowCreate(false)} 
          onCreated={fetchData} 
          members={members.filter(m => m.status === 'approved')}
        />
      )}
    </div>
  )
}
