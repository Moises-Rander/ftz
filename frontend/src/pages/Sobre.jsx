import { UserRound } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import PageHeader from '@/components/common/PageHeader'
import { Spinner, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useConteudo, useEquipe } from '@/hooks/useCms'
import { INSTITUICAO } from '@/lib/config'

const container = 'mx-auto max-w-6xl px-4 sm:px-6 lg:px-8'
const SECOES = ['MISSAO', 'VISAO', 'VALORES']

function Blocos() {
  const { data, isLoading, isError, refetch } = useConteudo()
  if (isLoading) return <Spinner />
  if (isError) return <ErrorState onRetry={refetch} />

  const blocos = (data || []).filter((b) => SECOES.includes(b.secao))
  if (blocos.length === 0)
    return <EmptyState message="Conteúdo institucional em atualização." />

  return (
    <div className="space-y-16">
      {blocos.map((b, i) => (
        <div
          key={b.id}
          className={`grid items-center gap-10 lg:grid-cols-2 ${i % 2 ? 'lg:[&>img]:order-first' : ''}`}
        >
          <div>
            <span className="text-sm font-semibold uppercase tracking-wide text-primary">
              {b.secao_display}
            </span>
            <h2 className="mt-1 text-3xl font-bold">{b.titulo}</h2>
            <p className="mt-4 whitespace-pre-line text-muted-foreground">{b.texto}</p>
          </div>
          {b.imagem && (
            <img src={b.imagem} alt={b.titulo} className="h-72 w-full rounded-2xl object-cover shadow-sm" />
          )}
        </div>
      ))}
    </div>
  )
}

function Equipe() {
  const { data, isLoading, isError, refetch } = useEquipe()
  return (
    <section className="mt-20">
      <h2 className="mb-8 text-center text-3xl font-bold">Nossa equipe</h2>
      {isLoading && <Spinner />}
      {isError && <ErrorState onRetry={refetch} />}
      {data &&
        (data.length === 0 ? (
          <EmptyState message="Em breve, apresentaremos nossa equipe." />
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {data.map((m) => (
              <Card key={m.id} className="text-center">
                <CardContent>
                  {m.foto ? (
                    <img src={m.foto} alt={m.nome} className="mx-auto h-24 w-24 rounded-full object-cover" />
                  ) : (
                    <span className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-primary/10 text-primary">
                      <UserRound className="h-10 w-10" />
                    </span>
                  )}
                  <p className="mt-4 font-semibold">{m.nome}</p>
                  <p className="text-sm text-primary">{m.cargo}</p>
                  {m.bio && <p className="mt-2 text-sm text-muted-foreground">{m.bio}</p>}
                </CardContent>
              </Card>
            ))}
          </div>
        ))}
    </section>
  )
}

export default function Sobre() {
  return (
    <>
      <PageHeader title={`Sobre a ${INSTITUICAO.sigla}`} subtitle={INSTITUICAO.descricao} />
      <div className={`${container} py-14`}>
        <Blocos />
        <Equipe />
      </div>
    </>
  )
}
