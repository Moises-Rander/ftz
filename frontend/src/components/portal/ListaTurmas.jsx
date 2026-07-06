import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { CardsSkeleton, ErrorState } from '@/components/common/StateComponents'
import { useMinhasMatriculas } from '@/hooks/useAluno'
import { tipoLabel } from '@/lib/format'

export default function ListaTurmas() {
  const { data, isLoading, isError, refetch } = useMinhasMatriculas()

  if (isLoading) return <CardsSkeleton count={3} />
  if (isError) return <ErrorState onRetry={refetch} />

  const aprovadas = (data || []).filter((m) => m.status === 'APROVADA')

  if (aprovadas.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
          <Sparkles className="h-10 w-10 text-primary" />
          <h2 className="text-xl font-semibold">Bem-vindo(a) ao Portal FTZ!</h2>
          <p className="max-w-md text-muted-foreground">
            Assim que sua matrícula for aprovada, o conteúdo acadêmico das suas turmas aparecerá
            aqui.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {aprovadas.map((m) => (
        <Card key={m.id} className="flex flex-col">
          <CardContent className="flex-1">
            <Badge variant="secondary">{tipoLabel(m.turma?.curso_tipo)}</Badge>
            <h3 className="mt-2 text-lg font-semibold">{m.turma?.curso_nome}</h3>
            <p className="text-sm text-muted-foreground">Turma {m.turma?.nome}</p>
          </CardContent>
          <CardContent className="pt-0">
            <Button asChild className="w-full">
              <Link to={`/portal/turmas/${m.turma?.id}`}>
                Acessar <ArrowRight className="ml-1 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
