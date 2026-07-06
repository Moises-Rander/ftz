import { Link } from 'react-router-dom'
import { ArrowRight, Presentation } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { CardsSkeleton, ErrorState } from '@/components/common/StateComponents'
import { useMinhasTurmasProfessor } from '@/hooks/useProfessor'
import { tipoLabel } from '@/lib/format'

export default function ListaTurmasProfessor() {
  const { data, isLoading, isError, refetch } = useMinhasTurmasProfessor()

  if (isLoading) return <CardsSkeleton count={3} />
  if (isError) return <ErrorState onRetry={refetch} />

  if (!data?.length) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
          <Presentation className="h-10 w-10 text-primary" />
          <p className="max-w-md text-muted-foreground">
            Você ainda não foi atribuído a nenhuma turma. Assim que a coordenação atribuir, suas
            turmas aparecerão aqui.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {data.map((t) => (
        <Card key={t.id} className="flex flex-col">
          <CardContent className="flex-1">
            <Badge variant="secondary">{tipoLabel(t.curso_tipo)}</Badge>
            <h3 className="mt-2 text-lg font-semibold">{t.curso_nome}</h3>
            <p className="text-sm text-muted-foreground">Turma {t.nome}</p>
          </CardContent>
          <CardContent className="pt-0">
            <Button asChild className="w-full">
              <Link to={`/portal-professor/turmas/${t.id}`}>
                Acessar <ArrowRight className="ml-1 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
