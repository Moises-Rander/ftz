import { Link } from 'react-router-dom'
import { CalendarDays, MapPin, FileText, PencilLine, Search } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import PageHeader from '@/components/common/PageHeader'
import { Spinner, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useEdicoes } from '@/hooks/useVestibular'
import { formatarData } from '@/lib/format'

const container = 'mx-auto max-w-6xl px-4 sm:px-6 lg:px-8'

const ETAPAS = [
  { titulo: 'Inscrição', texto: 'Preencha o formulário de inscrição na edição desejada.' },
  { titulo: 'Prova', texto: 'Compareça no local e data indicados para a avaliação.' },
  { titulo: 'Resultado', texto: 'Acompanhe o resultado e, se aprovado, efetive sua matrícula.' },
]

export default function Vestibular() {
  const { data, isLoading, isError, refetch } = useEdicoes()

  return (
    <>
      <PageHeader
        title="Vestibular"
        subtitle="Ingresse na Graduação da Faculdade de Teologia Zait através do nosso processo seletivo."
      />

      <div className={`${container} py-12`}>
        {/* Como funciona */}
        <div className="mb-14 grid gap-6 sm:grid-cols-3">
          {ETAPAS.map((e, i) => (
            <Card key={e.titulo}>
              <CardContent>
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary font-bold text-primary-foreground">
                  {i + 1}
                </span>
                <p className="mt-3 font-semibold">{e.titulo}</p>
                <p className="mt-1 text-sm text-muted-foreground">{e.texto}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <h2 className="mb-5 text-2xl font-bold">Edições disponíveis</h2>
        {isLoading && <Spinner />}
        {isError && <ErrorState onRetry={refetch} />}
        {data &&
          (data.length === 0 ? (
            <EmptyState message="Nenhuma edição de vestibular disponível no momento." />
          ) : (
            <div className="grid gap-4">
              {data.map((ed) => (
                <Card key={ed.id}>
                  <CardContent className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold">{ed.curso_nome}</h3>
                        {ed.resultado_publicado && (
                          <Badge variant="secondary">Resultado publicado</Badge>
                        )}
                      </div>
                      <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <CalendarDays className="h-4 w-4" /> Prova: {formatarData(ed.data_prova)}
                        </span>
                        <span className="flex items-center gap-1">
                          <MapPin className="h-4 w-4" /> {ed.local_prova}
                        </span>
                      </div>
                    </div>
                    <div className="flex shrink-0 flex-col gap-2 sm:flex-row">
                      {ed.inscricoes_abertas && (
                        <Button asChild>
                          <Link to={`/vestibular/${ed.id}/inscrever`}>
                            <PencilLine className="mr-2 h-4 w-4" /> Inscrever-se
                          </Link>
                        </Button>
                      )}
                      <Button asChild variant={ed.resultado_publicado ? 'default' : 'outline'}>
                        <Link to={`/vestibular/${ed.id}/resultado`}>
                          {ed.resultado_publicado ? (
                            <>
                              <FileText className="mr-2 h-4 w-4" /> Ver resultado
                            </>
                          ) : (
                            <>
                              <Search className="mr-2 h-4 w-4" /> Consultar status
                            </>
                          )}
                        </Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ))}
      </div>
    </>
  )
}
