import { CalendarDays, Clock } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useGradeCompleta } from '@/hooks/useAluno'
import { useTurma } from '@/hooks/useCursos'

const hhmm = (h) => (h ? String(h).slice(0, 5) : '')

const CORES_STATUS = {
  ATIVO: 'default',
  CONCLUIDO: 'outline',
  PENDENTE: 'secondary',
}

export default function AbaGrade({ turmaId }) {
  const { data, isLoading, isError, refetch } = useGradeCompleta(turmaId)
  const { data: turma } = useTurma(turmaId)

  if (isLoading) return <Spinner />
  if (isError || !data) return <ErrorState onRetry={refetch} />

  // Graduação: ciclos com grade
  if (data.tipo === 'GRADUACAO') {
    if (!data.ciclos?.length) return <EmptyState message="O calendário de ciclos será divulgado em breve." />
    return (
      <div className="space-y-5">
        {data.ciclos.map((ciclo) => (
          <Card key={ciclo.id} className={ciclo.is_ativo ? 'border-primary' : ''}>
            <CardContent>
              <div className="mb-3 flex items-center gap-2">
                <h3 className="font-semibold">Ciclo {ciclo.numero}</h3>
                {ciclo.is_ativo && <Badge>Ativo</Badge>}
              </div>
              {ciclo.grades?.length ? (
                <ul className="space-y-2">
                  {ciclo.grades.map((g) => (
                    <li key={g.id} className="flex flex-wrap items-center gap-3 text-sm">
                      <span className="font-medium">{g.disciplina_nome}</span>
                      <span className="flex items-center gap-1 text-muted-foreground">
                        <CalendarDays className="h-4 w-4" /> {g.dia_semana_display}
                      </span>
                      <span className="flex items-center gap-1 text-muted-foreground">
                        <Clock className="h-4 w-4" /> {hhmm(g.horario)}
                      </span>
                      <Badge variant="outline">{g.slots} slot(s)</Badge>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">Grade a definir.</p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  // Formação: módulos com status + horário semanal
  const horarios = turma?.horarios_formacao || []
  return (
    <div className="space-y-5">
      {horarios.length > 0 && (
        <Card>
          <CardContent>
            <h3 className="mb-2 font-semibold">Horário das aulas</h3>
            <ul className="space-y-1 text-sm text-muted-foreground">
              {horarios.map((h) => (
                <li key={h.id} className="flex items-center gap-2">
                  <Clock className="h-4 w-4" /> {h.dia_1_display} e {h.dia_2_display} às {hhmm(h.horario_inicio)} ({h.duracao_minutos} min)
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
      <div>
        <h3 className="mb-3 font-semibold">Módulos</h3>
        {data.modulos?.length ? (
          <ol className="space-y-3">
            {data.modulos.map((p) => (
              <li key={p.id}>
                <Card className={p.is_ativo ? 'border-primary' : ''}>
                  <CardContent className="flex items-start gap-4">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-sm font-bold">
                      {p.modulo?.ordem}
                    </span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{p.modulo?.nome}</p>
                        <Badge variant={CORES_STATUS[p.status] || 'secondary'}>{p.status_display}</Badge>
                      </div>
                      {p.modulo?.descricao && (
                        <p className="mt-1 text-sm text-muted-foreground">{p.modulo.descricao}</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </li>
            ))}
          </ol>
        ) : (
          <EmptyState message="Os módulos serão divulgados em breve." />
        )}
      </div>
    </div>
  )
}
