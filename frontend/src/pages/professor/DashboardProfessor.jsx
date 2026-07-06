import ListaTurmasProfessor from '@/components/professor/ListaTurmasProfessor'
import { useAuthStore } from '@/stores/useAuthStore'

export default function DashboardProfessor() {
  const user = useAuthStore((s) => s.user)
  const primeiroNome = (user?.nome || '').split(' ')[0]

  return (
    <div className="mx-auto max-w-6xl">
      <h1 className="text-2xl font-bold tracking-tight">
        Olá{primeiroNome ? `, Prof. ${primeiroNome}` : ''}! 👋
      </h1>
      <p className="mt-1 text-muted-foreground">Gerencie as turmas às quais você está atribuído.</p>
      <div className="mt-8">
        <h2 className="mb-4 text-lg font-semibold">Minhas turmas</h2>
        <ListaTurmasProfessor />
      </div>
    </div>
  )
}
