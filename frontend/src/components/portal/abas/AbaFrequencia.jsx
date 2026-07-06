import { Check, X, Ban } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useFrequencia } from '@/hooks/useAluno'
import { formatarData } from '@/lib/format'

export default function AbaFrequencia({ turmaId }) {
  const { data, isLoading, isError, refetch } = useFrequencia(turmaId)
  if (isLoading) return <Spinner />
  if (isError || !data) return <ErrorState onRetry={refetch} />

  return (
    <div className="space-y-5">
      <Card>
        <CardContent className="py-5 text-center">
          <p className="text-3xl font-bold text-primary">{data.percentual_presenca ?? 0}%</p>
          <p className="mt-1 text-sm text-muted-foreground">Presença acumulada</p>
        </CardContent>
      </Card>

      {data.aulas?.length ? (
        <Card>
          <CardContent className="divide-y p-0">
            {data.aulas.map((a) => (
              <div
                key={a.aula_id}
                className={`flex items-center justify-between px-4 py-3 ${
                  a.cancelada ? 'bg-muted/40' : ''
                }`}
              >
                <span className="text-sm">{formatarData(a.data)}</span>
                {a.cancelada ? (
                  <Badge variant="secondary" className="gap-1">
                    <Ban className="h-3.5 w-3.5" /> Cancelada
                  </Badge>
                ) : a.presente ? (
                  <Badge className="gap-1 border-green-600/40 bg-green-600/10 text-green-700" variant="outline">
                    <Check className="h-3.5 w-3.5" /> Presente
                  </Badge>
                ) : (
                  <Badge variant="outline" className="gap-1 border-destructive/40 text-destructive">
                    <X className="h-3.5 w-3.5" /> Ausente
                  </Badge>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      ) : (
        <EmptyState message="Nenhuma frequência registrada ainda." />
      )}
      <p className="text-xs text-muted-foreground">
        Aulas canceladas não entram no cálculo do percentual de presença.
      </p>
    </div>
  )
}
