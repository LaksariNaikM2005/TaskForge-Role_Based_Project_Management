import { useNavigate } from 'react-router-dom'
import dayjs from 'dayjs'

const priorityClass = { low: 'badge-low', medium: 'badge-medium', high: 'badge-high' }

export default function TaskCard({ task }) {
  const navigate = useNavigate()
  const isOverdue = task.due_date && dayjs(task.due_date).isBefore(dayjs(), 'day') && task.status !== 'Completed'

  return (
    <div className="task-card" onClick={() => navigate(`/tasks/${task.id}`)}>
      <div className="task-card-title">{task.title}</div>
      {task.description && <p className="text-xs text-muted" style={{ margin: 'var(--space-xs) 0' }}>{task.description.slice(0, 80)}{task.description.length > 80 ? '…' : ''}</p>}
      <div className="task-card-meta">
        <span className={`badge ${priorityClass[task.priority]}`}>{task.priority}</span>
        {task.department && <span className="badge" style={{ backgroundColor: 'rgba(255,255,255,0.1)', color: 'var(--primary)' }}>🏢 {task.department}</span>}
        {task.team && <span className="badge" style={{ backgroundColor: 'rgba(255,255,255,0.1)', color: 'var(--accent)' }}>👥 {task.team}</span>}
        <div className="flex flex-col gap-xs mt-xs">
          {task.creator && <span className="text-xs text-muted" title={`Created by: ${task.creator.email}`}>✍️ {task.creator.name}</span>}
          {task.assignee && <span className="text-xs text-primary" title={`Assigned to: ${task.assignee.email}`}>👤 {task.assignee.name}</span>}
        </div>
        {task.due_date && (
          <span className={`text-xs ${isOverdue ? 'badge badge-overdue' : 'text-muted'}`} style={{ marginLeft: 'auto' }}>
            📅 {dayjs(task.due_date).format('MMM D')}
          </span>
        )}
      </div>
    </div>
  )
}
