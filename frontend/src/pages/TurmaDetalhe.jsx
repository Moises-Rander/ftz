import { Link, useParams } from 'react-router-dom'
import { CalendarDays, Clock, GraduationCap, Layers, UserRound } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useTurma, useProfessoresDaTurma } from '@/hooks/useCursos'
import { tipoLabel, statusTurmaLabel } from '@/lib/format'

const container = 'mx-auto max-w-6xl px-4 sm:px-6 lg:px-8'
const hhmm = (h) => (h ? String(h).slice(0, 5) : '')

function GradeGraduacao({ ciclo }) {
  if (!ciclo) {
    return (
      <EmptyState message="Ainda não há um ciclo ativo. O calendário de aulas será divulgado em breve." />
    )
  }
  return (
    <div>
      <p className="mb-4 text-sm text-muted-foreground">
        Ciclo {ciclo.numero} — grade horária atual
      </p>
      {ciclo.grades && ciclo.grades.length > 0 ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {ciclo.grades.map((g) => (
            <Card key={g.id}>
              <CardContent>
                <p className="font-semibold">{g.disciplina_nome}</p>
                <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <CalendarDays className="h-4 w-4" /> {g.dia_semana_display}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-4 w-4" /> {hhmm(g.horario)}
                  </span>
                  <Badge variant="outline">{g.slots} slot(s)</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState message="A grade deste ciclo será divulgada em breve." />
      )}
    </div>
  )
}

function GradeFormacao({ turma }) {
  const horarios = turma.horarios_formacao || []
  return (
    <div className="space-y-6">
      <div>
        <h3 className="mb-3 font-semibold">Dias e horários das aulas</h3>
        {horarios.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {horarios.map((h) => (
              <Card key={h.id}>
                <CardContent className="flex items-center gap-3 text-sm">
                  <CalendarDays className="h-4 w-4 text-primary" />
                  <span>
                    {h.dia_1_display} e {h.dia_2_display} — {hhmm(h.horario_inicio)} ({h.duracao_minutos} min)
                  </span>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <EmptyState message="Os horários serão divulgados em breve." />
        )}
      </div>
      <div>
        <h3 className="mb-3 flex items-center gap-2 font-semibold">
          <Layers className="h-4 w-4 text-primary" /> Módulo em andamento
        </h3>
        {turma.modulo_ativo ? (
          <Card>
            <CardContent>
              <p className="font-semibold">
                {turma.modulo_ativo.ordem}. {turma.modulo_ativo.nome}
              </p>
              {turma.modulo_ativo.descricao && (
                <p className="mt-1 text-sm text-muted-foreground">{turma.modulo_ativo.descricao}</p>
              )}
            </CardContent>
          </Card>
        ) : (
          <EmptyState message="Nenhum módulo em andamento no momento." />
        )}
      </div>
    </div>
  )
}

function Professores({ turmaId }) {
  const { data, isLoading, isError, refetch } = useProfessoresDaTurma(turmaId)
  return (
    <section className="mt-12">
      <h2 className="mb-5 flex items-center gap-2 text-2xl font-bold">
        <UserRound className="h-6 w-6 text-primary" /> Professores
      </h2>
      {isLoading && <Spinner />}
      {isError && <ErrorState onRetry={refetch} />}
      {data &&
        (data.length === 0 ? (
          <EmptyState message="Professores a confirmar." />
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {data.map((p) => (
              <Card key={p.id}>
                <CardContent className="flex items-center gap-4">
                  {p.foto ? (
                    <img src={p.foto} alt={p.nome} className="h-16 w-16 rounded-full object-cover" />
                  ) : (
                    <span className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
                      <UserRound className="h-7 w-7" />
                    </span>
                  )}
                  <div>
                    <p className="font-semibold">{p.nome}</p>
                    <p className="text-sm text-muted-foreground">{p.titulacao}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ))}
    </section>
  )
}

export default function TurmaDetalhe() {
  const { id } = useParams()
  const { data: turma, isLoading, isError, refetch } = useTurma(id)

  if (isLoading)
    return (
      <div className={`${container} py-16`}>
        <Spinner label="Carregando turma..." />
      </div>
    )
  if (isError || !turma)
    return (
      <div className={`${container} py-16`}>
        <ErrorState onRetry={refetch} />
      </div>
    )

  const isGraduacao = turma.curso_tipo === 'GRADUACAO'

  return (
    <div className="pb-16">
      <section className="border-b bg-muted/40">
        <div className={`${container} py-12`}>
          <Badge variant="secondary">{tipoLabel(turma.curso_tipo)}</Badge>
          <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            {turma.nome || `Turma #${turma.id}`}
          </h1>
          <div className="mt-4 flex flex-wrap items-center gap-2">
            <Badge variant={turma.status === 'ABERTA' ? 'default' : 'secondary'}>
              {statusTurmaLabel(turma.status)}
            </Badge>
            <Badge variant={turma.vagas_disponiveis > 0 ? 'outline' : 'destructive'}>
              {turma.vagas_disponiveis > 0
                ? `${turma.vagas_disponiveis} vaga(s) disponível(is)`
                : 'Vagas esgotadas'}
            </Badge>
          </div>
          <div className="mt-6">
            {turma.status === 'ABERTA' ? (
              <Button asChild size="lg">
                <Link to={`/matricula/${turma.id}`}>
                  <GraduationCap className="mr-2 h-5 w-5" /> Realizar matrícula
                </Link>
              </Button>
            ) : (
              <Button size="lg" disabled>
                <GraduationCap className="mr-2 h-5 w-5" /> Vagas esgotadas
              </Button>
            )}
          </div>
        </div>
      </section>

      <div className={`${container} pt-12`}>
        <h2 className="mb-5 text-2xl font-bold">Calendário e aulas</h2>
        {isGraduacao ? <GradeGraduacao ciclo={turma.ciclo_ativo} /> : <GradeFormacao turma={turma} />}
        <Professores turmaId={id} />
      </div>
    </div>
  )
}
