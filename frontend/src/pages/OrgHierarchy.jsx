import { useState, useEffect } from 'react'
import { orgAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

export default function OrgHierarchy() {
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [org, setOrg] = useState(null)
  const { user } = useAuth()
  const { toast } = useToast()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [orgRes, membersRes] = await Promise.all([
          orgAPI.getMe(),
          orgAPI.members()
        ])
        setOrg(orgRes.data)
        setMembers(membersRes.data)
      } catch { toast.error('Failed to load organization data') }
      finally { setLoading(false) }
    }
    fetchData()
  }, [])

  if (loading) return <div className="page-content"><div className="spinner" /></div>

  const roles = ['ceo', 'head', 'leader', 'employee']

  return (
    <div className="page-content">
      <div className="flex justify-between items-center mb-lg">
        <div>
          <h1>{org?.name} Structure</h1>
          <p className="text-muted text-sm">Your Referral Code: <strong className="text-primary" style={{ letterSpacing: 1 }}>{user?.referral_code}</strong></p>
        </div>
      </div>

      <div className="grid gap-lg">
        {roles.map(role => {
          const roleMembers = members.filter(m => m.role === role && m.status === 'approved')
          if (roleMembers.length === 0) return null
          
          return (
            <div key={role} className="card">
              <h3 className="mb-md" style={{ textTransform: 'capitalize', borderBottom: '1px solid var(--border)', paddingBottom: 'var(--space-xs)' }}>
                {role}s ({roleMembers.length})
              </h3>
              <div className="flex flex-wrap gap-md">
                {roleMembers.map(m => (
                  <div key={m.id} className="flex items-center gap-sm" style={{ background: 'var(--bg-app)', padding: 'var(--space-sm) var(--space-md)', borderRadius: 8, border: '1px solid var(--border)', minWidth: 200 }}>
                    <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600 }}>
                      {m.name[0]}
                    </div>
                    <div>
                      <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{m.name} {m.id === user?.id && '(You)'}</div>
                      <div className="text-xs text-muted">{m.email}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
