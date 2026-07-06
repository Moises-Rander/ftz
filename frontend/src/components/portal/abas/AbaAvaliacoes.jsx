import { Card, CardContent } from '@/components/ui/card'
import { Spinner, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useAvaliacoes } from '@/hooks/useAluno'
import { formatarData } from '@/lib/format'

export default function AbaAvaliacoes({ turmaId }) {
  const { data, isLoading, isError, refetch } = useAvaliacoes(turmaId)
  if (isLoading) return <Spinner />
  if (isError || !data) return <ErrorState onRetry={refetch} />
  if (data.length === 0) return <EmptyState message="Nenhuma avaliação cadastrada ainda." />

  return (
    <Card>
      <CardContent className="divide-y p-0">
        {data.map((a) => {
          const lancada = a.minha_nota !== 'não lançado'
          return (
            <div key={a.id} className="flex items-center justify-between gap-4 px-4 py-4">
              <div>
                <p className="font-medium">{a.titulo}</p>
                <p className="text-xs text-muted-foreground">{formatarData(a.data)}</p>
                {a.descricao && (
                  <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{a.descricao}</p>
                )}
              </div>
              <div className="shrink-0 text-right">
                {lancada ? (
                  <p className="text-lg font-semibold">
                    {a.minha_nota}
                    <span className="text-sm font-normal text-muted-foreground"> / {a.nota_maxima}</span>
                  </p>
                ) : (
                  <p className="text-sm text-muted-foreground">Aguardando lançamento</p>
                )}
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
