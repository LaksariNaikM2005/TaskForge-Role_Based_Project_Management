import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

export default function Register() {
  const [mode, setMode] = useState('join') // 'join' or 'create'
  const [form, setForm] = useState({ 
    name: '', 
    email: '', 
    password: '', 
    organization_name: '', 
    referral_code: '', 
    department: '',
    team: '' 
  })
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = { ...form }
      // Trim all string values
      Object.keys(data).forEach(key => {
        if (typeof data[key] === 'string') data[key] = data[key].trim()
      })

      if (mode === 'join') delete data.organization_name
      else delete data.referral_code
      
      await register(data)
      if (mode === 'create') {
        toast.success('Organization created!')
        navigate('/dashboard')
      } else {
        toast.info('Registration successful! Please wait for admin approval.')
        navigate('/login')
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">⚡ TaskForge v2</div>
        <p className="auth-subtitle">Join or create your workspace</p>
        
        <div className="flex gap-sm mb-lg" style={{ background: 'var(--bg-card)', padding: 4, borderRadius: 8 }}>
          <button 
            className={`btn btn-sm full-width ${mode === 'join' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setMode('join')}
          >Join Org</button>
          <button 
            className={`btn btn-sm full-width ${mode === 'create' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setMode('create')}
          >Create Org</button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input className="form-input" type="text" placeholder="John Doe" value={form.name} onChange={e => set('name', e.target.value)} required />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="form-input" type="email" placeholder="you@company.com" value={form.email} onChange={e => set('email', e.target.value)} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input className="form-input" type="password" placeholder="••••••••" value={form.password} onChange={e => set('password', e.target.value)} minLength={6} required />
          </div>

          {mode === 'create' ? (
            <div className="form-group">
              <label className="form-label">Organization Name</label>
              <input className="form-input" type="text" placeholder="Acme Corp" value={form.organization_name} onChange={e => set('organization_name', e.target.value)} required />
            </div>
          ) : (
            <>
              <div className="form-group">
                <label className="form-label">Referral Code</label>
                <input className="form-input" type="text" placeholder="ABCD1234" value={form.referral_code} onChange={e => set('referral_code', e.target.value)} required />
              </div>
              <div className="form-group animate-slide-in">
                <label className="form-label">Department (Optional)</label>
                <input 
                  className="form-input" 
                  type="text" 
                  placeholder="e.g. Engineering, Sales" 
                  value={form.department} 
                  onChange={e => set('department', e.target.value)} 
                />
                <p className="text-xs text-muted mt-xs">Required if you are joining as a Department Head.</p>
              </div>
              <div className="form-group animate-slide-in">
                <label className="form-label">Team (Optional)</label>
                <input 
                  className="form-input" 
                  type="text" 
                  placeholder="e.g. Backend, UI/UX" 
                  value={form.team} 
                  onChange={e => set('team', e.target.value)} 
                />
                <p className="text-xs text-muted mt-xs">Required if you are joining as a Team Leader.</p>
              </div>
            </>
          )}

          <button className="btn btn-primary full-width" type="submit" disabled={loading}>
            {loading ? <span className="spinner" /> : mode === 'create' ? 'Create Organization →' : 'Register →'}
          </button>
        </form>
        <p className="text-sm text-muted" style={{ textAlign: 'center', marginTop: 'var(--space-md)' }}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
