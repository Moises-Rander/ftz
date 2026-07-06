import ListaTurmas from '@/components/portal/ListaTurmas'
import { useAuthStore } from '@/stores/useAuthStore'

export default function Dashboard() {
  const user = useAuthStore((s) => s.user)
  const primeiroNome = (user?.nome || '').split(' ')[0]

  return (
    <div className="mx-auto max-w-6xl">
      <h1 className="text-2xl font-bold tracking-tight">
        Olá{primeiroNome ? `, ${primeiroNome}` : ''}! 👋
      </h1>
      <p className="mt-1 text-muted-foreground">Acesse suas turmas e acompanhe sua vida acadêmica.</p>
      <div className="mt-8">
        <h2 className="mb-4 text-lg font-semibold">Minhas turmas</h2>
        <ListaTurmas />
      </div>
    </div>
  )
}
