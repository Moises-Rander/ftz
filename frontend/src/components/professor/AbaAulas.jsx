import { Ban, CalendarDays, CheckCircle2, Clock } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useTurmaAulas } from '@/hooks/useProfessor'
import { formatarData } from '@/lib/format'
import PainelFrequencia from './PainelFrequencia'

const hhmm = (h) => (h ? String(h).slice(0, 5) : '')

export default function AbaAulas({ turmaId }) {
  const { data, isLoading, isError, refetch } = useTurmaAulas(turmaId)
  if (isLoading) return <Spinner />
  if (isError) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <EmptyState message="Nenhuma aula cadastrada nesta turma." />

  return (
    <div className="space-y-3">
      {data.map((aula) => (
        <Card key={aula.id} className={aula.cancelada ? 'opacity-70' : ''}>
          <CardContent className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-medium">{aula.disciplina_nome || aula.modulo_nome}</p>
              <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <CalendarDays className="h-4 w-4" /> {formatarData(aula.data)}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" /> {hhmm(aula.horario_inicio)}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {aula.cancelada ? (
                <Badge variant="secondary" className="gap-1">
                  <Ban className="h-3.5 w-3.5" /> Cancelada
                </Badge>
              ) : (
                <>
                  {aula.frequencia_lancada ? (
                    <Badge className="gap-1 border-green-600/40 text-green-700" variant="outline">
                      <CheckCircle2 className="h-3.5 w-3.5" /> Lançada
                    </Badge>
                  ) : (
                    <Badge variant="secondary">Pendente</Badge>
                  )}
                  <PainelFrequencia aula={aula} turmaId={turmaId} />
                </>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
