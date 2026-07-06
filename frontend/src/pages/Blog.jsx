import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { CalendarDays, ArrowRight, Newspaper } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter } from '@/components/ui/card'
import PageHeader from '@/components/common/PageHeader'
import { CardsSkeleton, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { usePosts } from '@/hooks/useCms'
import { formatarData } from '@/lib/format'

const PAGINA = 6

export default function Blog() {
  const [params, setParams] = useSearchParams()
  const categoria = params.get('categoria') || 'TODAS'
  const [visiveis, setVisiveis] = useState(PAGINA)

  // Busca todos os publicados e filtra por categoria no cliente (permite montar as chips).
  const { data, isLoading, isError, refetch } = usePosts()

  const categorias = useMemo(() => {
    const set = new Set((data || []).map((p) => p.categoria).filter(Boolean))
    return ['TODAS', ...set]
  }, [data])

  const filtrados = useMemo(
    () =>
      categoria === 'TODAS'
        ? data || []
        : (data || []).filter((p) => p.categoria === categoria),
    [data, categoria]
  )

  const setCategoria = (c) => {
    const novo = new URLSearchParams(params)
    if (c === 'TODAS') novo.delete('categoria')
    else novo.set('categoria', c)
    setParams(novo, { replace: true })
    setVisiveis(PAGINA)
  }

  return (
    <>
      <PageHeader title="Blog e Notícias" subtitle="Reflexões, eventos e novidades da Faculdade de Teologia Zait." />
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
        {categorias.length > 1 && (
          <div className="mb-8 flex flex-wrap gap-2">
            {categorias.map((c) => (
              <Button
                key={c}
                variant={categoria === c ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCategoria(c)}
              >
                {c === 'TODAS' ? 'Todas' : c}
              </Button>
            ))}
          </div>
        )}

        {isLoading && <CardsSkeleton count={6} />}
        {isError && <ErrorState onRetry={refetch} />}
        {data &&
          (filtrados.length === 0 ? (
            <EmptyState message="Nenhum post publicado nesta categoria." />
          ) : (
            <>
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {filtrados.slice(0, visiveis).map((p) => (
                  <Card key={p.id} className="flex flex-col overflow-hidden pt-0">
                    <div className="h-44 w-full overflow-hidden bg-muted">
                      {p.imagem ? (
                        <img src={p.imagem} alt={p.titulo} className="h-full w-full object-cover" loading="lazy" />
                      ) : (
                        <div className="flex h-full items-center justify-center text-muted-foreground">
                          <Newspaper className="h-10 w-10" />
                        </div>
                      )}
                    </div>
                    <CardContent className="flex-1">
                      {p.categoria && <Badge variant="secondary">{p.categoria}</Badge>}
                      <h3 className="mt-2 line-clamp-2 text-lg font-semibold">{p.titulo}</h3>
                      <p className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
                        <CalendarDays className="h-3.5 w-3.5" /> {formatarData(p.data_publicacao)}
                      </p>
                      {p.resumo && <p className="mt-2 line-clamp-3 text-sm text-muted-foreground">{p.resumo}</p>}
                    </CardContent>
                    <CardFooter>
                      <Button asChild variant="link" className="px-0">
                        <Link to={`/blog/${p.slug}`}>
                          Ler mais <ArrowRight className="ml-1 h-4 w-4" />
                        </Link>
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
              {visiveis < filtrados.length && (
                <div className="mt-10 text-center">
                  <Button variant="outline" onClick={() => setVisiveis((v) => v + PAGINA)}>
                    Carregar mais
                  </Button>
                </div>
              )}
            </>
          ))}
      </div>
    </>
  )
}
