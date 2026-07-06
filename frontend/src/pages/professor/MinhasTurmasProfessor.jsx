import ListaTurmasProfessor from '@/components/professor/ListaTurmasProfessor'

export default function MinhasTurmasProfessor() {
  return (
    <div className="mx-auto max-w-6xl">
      <h1 className="text-2xl font-bold tracking-tight">Minhas turmas</h1>
      <div className="mt-6">
        <ListaTurmasProfessor />
      </div>
    </div>
  )
}
