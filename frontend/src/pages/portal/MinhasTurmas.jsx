import ListaTurmas from '@/components/portal/ListaTurmas'

export default function MinhasTurmas() {
  return (
    <div className="mx-auto max-w-6xl">
      <h1 className="text-2xl font-bold tracking-tight">Minhas turmas</h1>
      <div className="mt-6">
        <ListaTurmas />
      </div>
    </div>
  )
}
