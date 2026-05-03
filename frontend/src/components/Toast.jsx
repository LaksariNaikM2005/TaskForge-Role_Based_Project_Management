import { useToast } from '../context/ToastContext'

const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' }

export default function Toast() {
  const { toasts } = useToast()
  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast ${t.type}`}>
          <span>{icons[t.type]}</span>
          <span>{t.message}</span>
        </div>
      ))}
    </div>
  )
}
