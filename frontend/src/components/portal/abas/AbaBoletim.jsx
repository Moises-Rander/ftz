import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner, ErrorState } from '@/components/common/StateComponents'
import { useBoletim } from '@/hooks/useAluno'
import { formatarData } from '@/lib/format'

const STATUS_TRAB = {
  PENDENTE: { label: 'Pendente', variant: 'secondary' },
  ENTREGUE: { label: 'Entregue', variant: 'outline' },
  CORRIGIDO: { label: 'Corrigido', variant: 'default' },
}

function Metric({ label, value }) {
  return (
    <Card>
      <CardContent className="py-5 text-center">
        <p className="text-3xl font-bold text-primary">{value}</p>
        <p className="mt-1 text-sm text-muted-foreground">{label}</p>
      </CardContent>
    </Card>
  )
}

export default function AbaBoletim({ turmaId }) {
  const { data, isLoading, isError, refetch } = useBoletim(turmaId)
  if (isLoading) return <Spinner />
  if (isError || !data) return <ErrorState onRetry={refetch} />

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2">
        <Metric label="Presença geral" value={`${data.percentual_presenca ?? 0}%`} />
        <Metric
          label="Média geral"
          value={data.media_geral != null ? `${data.media_geral}%` : '—'}
        />
      </div>

      <div>
        <h3 className="mb-3 font-semibold">Avaliações</h3>
        <Card>
          <CardContent className="divide-y p-0">
            {data.avaliacoes?.length ? (
              data.avaliacoes.map((a) => (
                <div key={a.avaliacao_id} className="flex items-center justify-between px-4 py-3">
                  <div>
                    <p className="font-medium">{a.titulo}</p>
                    <p className="text-xs text-muted-foreground">{formatarData(a.data)}</p>
                  </div>
                  <span className="text-sm">
                    {a.nota != null ? (
                      <strong>{a.nota}</strong>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}{' '}
                    <span className="text-muted-foreground">/ {a.nota_maxima}</span>
                  </span>
                </div>
              ))
            ) : (
              <p className="px-4 py-6 text-center text-sm text-muted-foreground">Sem avaliações.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <div>
        <h3 className="mb-3 font-semibold">Trabalhos</h3>
        <Card>
          <CardContent className="divide-y p-0">
            {data.trabalhos?.length ? (
              data.trabalhos.map((t) => {
                const st = STATUS_TRAB[t.status] || STATUS_TRAB.PENDENTE
                return (
                  <div key={t.trabalho_id} className="flex items-center justify-between px-4 py-3">
                    <div>
                      <p className="font-medium">{t.titulo}</p>
                      <p className="text-xs text-muted-foreground">
                        Prazo: {formatarData(t.prazo_entrega, true)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {t.nota != null && <span className="text-sm font-semibold">{t.nota}</span>}
                      <Badge variant={st.variant}>{st.label}</Badge>
                    </div>
                  </div>
                )
              })
            ) : (
              <p className="px-4 py-6 text-center text-sm text-muted-foreground">Sem trabalhos.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
