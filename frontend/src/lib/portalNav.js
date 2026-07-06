import { LayoutDashboard, GraduationCap, UserRound } from 'lucide-react'

export const NAV_ALUNO = [
  { label: 'Dashboard', to: '/portal/dashboard', icon: LayoutDashboard },
  { label: 'Minhas Turmas', to: '/portal/turmas', icon: GraduationCap, end: true },
  { label: 'Perfil', to: '/portal/perfil', icon: UserRound },
]

export const NAV_PROFESSOR = [
  { label: 'Dashboard', to: '/portal-professor/dashboard', icon: LayoutDashboard },
  { label: 'Minhas Turmas', to: '/portal-professor/turmas', icon: GraduationCap, end: true },
  { label: 'Perfil', to: '/portal-professor/perfil', icon: UserRound },
]
