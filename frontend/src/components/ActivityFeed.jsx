import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime)

const actionLabels = {
  created_project: '🏗️ created project',
  updated_project: '✏️ updated project',
  created_task:    '✅ created task',
  updated_task:    '🔄 updated task',
  deleted_task:    '🗑️ deleted task',
  added_member:    '👤 added member',
  removed_member:  '❌ removed member',
}

export default function ActivityFeed({ logs }) {
  if (!logs?.length) return <div className="text-muted text-sm" style={{ textAlign: 'center', padding: 'var(--space-lg)' }}>No activity yet</div>

  return (
    <div>
      {logs.map(log => (
        <div key={log.id} className="activity-item">
          <div className="activity-dot" />
          <div style={{ flex: 1 }}>
            <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{log.user?.name ?? 'Someone'}</span>
            <span className="text-sm text-muted"> {actionLabels[log.action] ?? log.action}</span>
            <div className="text-xs text-muted" style={{ marginTop: 2 }}>{dayjs(log.created_at).fromNow()}</div>
          </div>
        </div>
      ))}
    </div>
  )
}
