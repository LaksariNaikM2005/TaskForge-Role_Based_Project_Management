import React from 'react'

export default function OrgStructureView({ structure }) {
  if (!structure || !structure.departments || structure.departments.length === 0) {
    return (
      <div className="card" style={{ padding: 'var(--space-lg)', textAlign: 'center' }}>
        <p className="text-muted">No organizational structure defined yet.</p>
      </div>
    )
  }

  return (
    <div className="org-structure">
      {structure.departments.map(dept => (
        <div key={dept.name} className="dept-card card mb-md">
          <div className="dept-header flex justify-between items-center mb-md pb-xs" style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <div>
              <h3 style={{ color: 'var(--primary)', marginBottom: 2 }}>🏢 {dept.name}</h3>
              <p className="text-xs text-muted">Department</p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <p className="text-sm"><strong>{dept.head_name || 'No Head'}</strong></p>
              <p className="text-xs text-muted">Department Head</p>
            </div>
          </div>
          
          <div className="teams-grid grid grid-3 gap-sm">
            {dept.teams && dept.teams.length > 0 ? (
              dept.teams.map(team => (
                <div key={team.name} className="team-item p-sm" style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 8 }}>
                  <p className="text-sm font-bold" style={{ color: 'var(--accent)' }}>👥 {team.name}</p>
                  <p className="text-xs text-muted">Lead: {team.leader_name || 'TBD'}</p>
                </div>
              ))
            ) : (
              <p className="text-xs text-muted col-span-3" style={{ fontStyle: 'italic' }}>No teams assigned to this department.</p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
