export default function StatCard({ title, value, icon, color }) {
  return (
    <div className="stat-card" style={{ borderTop: `4px solid ${color}` }}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-number">{value ?? '—'}</div>
      <div className="stat-label">{title}</div>
    </div>
  )
}
