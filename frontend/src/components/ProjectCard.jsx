import { Link } from 'react-router-dom'

export default function ProjectCard({ project }) {
  return (
    <Link to={`/projects/${project.id}`} className="project-card">
      <div className="flex items-center justify-between">
        <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>{project.title}</h3>
        <span className={`badge badge-${project.my_role}`}>{project.my_role}</span>
      </div>
      {project.description && (
        <p className="text-sm text-muted" style={{ lineClamp: 2, overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
          {project.description}
        </p>
      )}
      <div className="flex gap-md text-xs text-muted" style={{ marginTop: 'auto' }}>
        <span>👥 {project.member_count} members</span>
        <span>📋 {project.task_count ?? '—'} tasks</span>
      </div>
    </Link>
  )
}
