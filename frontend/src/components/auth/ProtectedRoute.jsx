import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/useAuthStore'

// Protege rotas autenticadas. allowedRole restringe por perfil (ex.: 'ALUNO').
export default function ProtectedRoute({ children, allowedRole }) {
  const location = useLocation()
  const access = useAuthStore((s) => s.access)
  const user = useAuthStore((s) => s.user)

  if (!access) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedRole && user?.role !== allowedRole) {
    // Perfil incompatível → envia ao destino apropriado.
    if (user?.role === 'PROFESSOR') {
      return <Navigate to="/portal-professor/dashboard" replace />
    }
    return <Navigate to="/" replace />
  }

  return children
}
