import { Link, useParams } from 'react-router-dom'
import { Clock, BookOpen, Layers, ArrowRight, Users } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useCurso, useTurmasDoCurso } from '@/hooks/useCursos'
import { tipoLabel, cargaHorariaLabel, statusTurmaLabel } from '@/lib/format'

const container = 'mx-auto max-w-6xl px-4 sm:px-6 lg:px-8'

function TurmasSection({ cursoId }) {
  const { data, isLoading, isError, refetch } = useTurmasDoCurso(cursoId)
  return (
    <section className="mt-12">
      <h2 className="mb-5 flex items-center gap-2 text-2xl font-bold">
        <Users className="h-6 w-6 text-primary" /> Turmas
      </h2>
      {isLoading && <Spinner />}
      {isError && <ErrorState onRetry={refetch} />}
      {data &&
        (data.length === 0 ? (
          <EmptyState message="Nenhuma turma aberta no momento. Volte em breve!" />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {data.map((t) => (
              <Card key={t.id}>
                <CardContent className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-semibold">{t.nome || `Turma #${t.id}`}</p>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <Badge variant={t.status === 'ABERTA' ? 'default' : 'secondary'}>
                        {statusTurmaLabel(t.status)}
                      </Badge>
                      <Badge variant={t.vagas_disponiveis > 0 ? 'outline' : 'destructive'}>
                        {t.vagas_disponiveis > 0
                          ? `${t.vagas_disponiveis} vaga(s)`
                          : 'Vagas esgotadas'}
                      </Badge>
                    </div>
                  </div>
                  <Button asChild size="sm" variant="outline">
                    <Link to={`/turmas/${t.id}`}>
                      Ver detalhes <ArrowRight className="ml-1 h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        ))}
    </section>
  )
}

export default function CursoDetalhe() {
  const { id } = useParams()
  const { data: curso, isLoading, isError, refetch } = useCurso(id)

  if (isLoading)
    return (
      <div className={`${container} py-16`}>
        <Spinner label="Carregando curso..." />
      </div>
    )
  if (isError || !curso)
    return (
      <div className={`${container} py-16`}>
        <ErrorState onRetry={refetch} />
      </div>
    )

  const isGraduacao = curso.tipo === 'GRADUACAO'

  return (
    <div className="pb-16">
      {/* Cabeçalho do curso */}
      <section className="border-b bg-muted/40">
        <div className={`${container} grid gap-8 py-12 lg:grid-cols-2`}>
          <div>
            <Badge variant="secondary">{tipoLabel(curso.tipo)}</Badge>
            <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">{curso.nome}</h1>
            <div className="mt-4 flex items-center gap-2 text-muted-foreground">
              <Clock className="h-4 w-4" /> {cargaHorariaLabel(curso.carga_horaria)}
            </div>
            {curso.descricao && (
              <p className="mt-5 whitespace-pre-line text-muted-foreground">{curso.descricao}</p>
            )}
          </div>
          {curso.imagem && (
            <img src={curso.imagem} alt={curso.nome} className="h-72 w-full rounded-2xl object-cover shadow-sm" />
          )}
        </div>
      </section>

      <div className={`${container} pt-12`}>
        {/* Estrutura curricular */}
        {isGraduacao ? (
          <section>
            <h2 className="mb-5 flex items-center gap-2 text-2xl font-bold">
              <BookOpen className="h-6 w-6 text-primary" /> Disciplinas
            </h2>
            {curso.disciplinas && curso.disciplinas.length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {curso.disciplinas.map((d) => (
                  <Card key={d.id}>
                    <CardContent>
                      <p className="font-semibold">{d.nome}</p>
                      {d.descricao && (
                        <p className="mt-1 line-clamp-3 text-sm text-muted-foreground">{d.descricao}</p>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState message="As disciplinas serão divulgadas em breve." />
            )}
          </section>
        ) : (
          <section>
            <h2 className="mb-5 flex items-center gap-2 text-2xl font-bold">
              <Layers className="h-6 w-6 text-primary" /> Módulos
            </h2>
            {curso.modulos && curso.modulos.length > 0 ? (
              <ol className="space-y-3">
                {curso.modulos.map((m, i) => (
                  <li key={m.id}>
                    <Card>
                      <CardContent className="flex gap-4">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-bold text-primary-foreground">
                          {m.ordem ?? i + 1}
                        </span>
                        <div>
                          <p className="font-semibold">{m.nome}</p>
                          {m.descricao && (
                            <p className="mt-1 text-sm text-muted-foreground">{m.descricao}</p>
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
          </section>
        )}

        <TurmasSection cursoId={id} />
      </div>
    </div>
  )
}
