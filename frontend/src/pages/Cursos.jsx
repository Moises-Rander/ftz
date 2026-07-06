import { useSearchParams } from 'react-router-dom'
import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import PageHeader from '@/components/common/PageHeader'
import CursoCard from '@/components/cursos/CursoCard'
import { CardsSkeleton, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useCursos } from '@/hooks/useCursos'

const TIPOS = [
  { value: 'TODOS', label: 'Todos' },
  { value: 'GRADUACAO', label: 'Graduação' },
  { value: 'FORMACAO', label: 'Formação' },
]

export default function Cursos() {
  const [params, setParams] = useSearchParams()
  const tipo = params.get('tipo') || 'TODOS'
  const search = params.get('search') || ''

  const { data, isLoading, isError, refetch } = useCursos({ tipo, search })

  const atualizar = (chave, valor) => {
    const novo = new URLSearchParams(params)
    if (valor && valor !== 'TODOS') novo.set(chave, valor)
    else novo.delete(chave)
    setParams(novo, { replace: true })
  }

  return (
    <>
      <PageHeader
        title="Nossos cursos"
        subtitle="Explore os cursos de Graduação e Formação da Faculdade de Teologia Zait."
      />
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        {/* Filtros */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap gap-2">
            {TIPOS.map((t) => (
              <Button
                key={t.value}
                variant={tipo === t.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => atualizar('tipo', t.value)}
              >
                {t.label}
              </Button>
            ))}
          </div>
          <div className="relative w-full sm:max-w-xs">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => atualizar('search', e.target.value)}
              placeholder="Buscar por nome..."
              className="pl-9"
            />
          </div>
        </div>

        {isLoading && <CardsSkeleton count={6} />}
        {isError && <ErrorState onRetry={refetch} />}
        {data &&
          (data.length === 0 ? (
            <EmptyState message="Nenhum curso encontrado com esses filtros." />
          ) : (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {data.map((curso) => (
                <CursoCard key={curso.id} curso={curso} mostrarVagas />
              ))}
            </div>
          ))}
      </div>
    </>
  )
}
