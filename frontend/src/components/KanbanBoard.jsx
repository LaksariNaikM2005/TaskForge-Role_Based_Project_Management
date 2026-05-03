import TaskCard from './TaskCard'

const columns = [
  { key: 'todo',  label: 'To Do',       color: 'var(--text-muted)' },
  { key: 'doing', label: 'In Progress',  color: 'var(--primary)'   },
  { key: 'done',  label: 'Completed',    color: 'var(--success)'   },
]

export default function KanbanBoard({ tasks, isAdmin }) {
  const grouped = columns.reduce((acc, col) => {
    acc[col.key] = tasks.filter(t => t.status === col.key)
    return acc
  }, {})

  return (
    <div className="kanban-board">
      {columns.map(col => (
        <div key={col.key} className="kanban-column">
          <div className="kanban-header">
            <span className="kanban-title" style={{ color: col.color }}>{col.label}</span>
            <span className="kanban-count">{grouped[col.key]?.length || 0}</span>
          </div>
          <div className="kanban-tasks">
            {grouped[col.key]?.length === 0 ? (
              <div style={{ textAlign: 'center', padding: 'var(--space-xl)', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No tasks here
              </div>
            ) : (
              grouped[col.key].map(task => <TaskCard key={task.id} task={task} />)
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
