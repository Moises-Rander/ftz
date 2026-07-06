import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { ChevronDown, ChevronUp, Download, Clock, AlertTriangle } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Spinner, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useTurmaTrabalhos, useTrabalhoEntregas, useCorrigirEntrega } from '@/hooks/useProfessor'
import { formatarData } from '@/lib/format'

function CorrecaoEntrega({ entrega, trabalhoId }) {
  const corrigida = entrega.nota != null
  const [editando, setEditando] = useState(!corrigida)
  const [nota, setNota] = useState(entrega.nota ?? '')
  const [feedback, setFeedback] = useState(entrega.feedback ?? '')
  const corrigir = useCorrigirEntrega(entrega.id)
  const qc = useQueryClient()

  const salvar = () => {
    if (nota === '' || Number(nota) < 0) {
      toast.error('Informe uma nota válida.')
      return
    }
    corrigir.mutate(
      { nota: Number(nota), feedback },
      {
        onSuccess: () => {
          toast.success('Correção salva.')
          qc.invalidateQueries({ queryKey: ['prof-entregas', trabalhoId] })
          setEditando(false)
        },
        onError: () => toast.error('Não foi possível salvar a correção.'),
      }
    )
  }

  if (!editando) {
    return (
      <div className="rounded-md bg-muted/50 p-3 text-sm">
        <p>
          Nota: <strong>{entrega.nota}</strong>
        </p>
        {entrega.feedback && <p className="mt-1 text-muted-foreground">{entrega.feedback}</p>}
        <Button size="sm" variant="ghost" className="mt-2 px-0" onClick={() => setEditando(true)}>
          Editar correção
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-3 rounded-md border p-3">
      <div className="space-y-1.5">
        <Label>Nota</Label>
        <Input type="number" min="0" step="0.1" value={nota} onChange={(e) => setNota(e.target.value)} className="w-28" />
      </div>
      <div className="space-y-1.5">
        <Label>Feedback</Label>
        <Textarea rows={3} value={feedback} onChange={(e) => setFeedback(e.target.value)} />
      </div>
      <Button size="sm" onClick={salvar} disabled={corrigir.isPending}>
        {corrigir.isPending ? 'Salvando...' : 'Salvar correção'}
      </Button>
    </div>
  )
}

function EntregasList({ trabalhoId }) {
  const { data, isLoading, isError, refetch } = useTrabalhoEntregas(trabalhoId, true)
  if (isLoading) return <Spinner />
  if (isError) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <p className="py-4 text-sm text-muted-foreground">Nenhuma entrega recebida.</p>

  return (
    <div className="space-y-3">
      {data.map((e) => (
        <div key={e.id} className="rounded-lg border p-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="font-medium">{e.aluno_nome}</p>
              <p className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3.5 w-3.5" /> {formatarData(e.data_hora_entrega, true)}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {e.entregue_em_atraso && (
                <Badge variant="outline" className="gap-1 border-amber-600/40 text-amber-700">
                  <AlertTriangle className="h-3.5 w-3.5" /> Em atraso
                </Badge>
              )}
              {e.nota != null ? (
                <Badge className="border-green-600/40 text-green-700" variant="outline">Corrigido</Badge>
              ) : (
                <Badge variant="secondary">Aguardando correção</Badge>
              )}
              {e.arquivo && (
                <Button asChild size="sm" variant="ghost">
                  <a href={e.arquivo} target="_blank" rel="noreferrer">
                    <Download className="mr-1 h-4 w-4" /> Baixar
                  </a>
                </Button>
              )}
            </div>
          </div>
          <div className="mt-3">
            <CorrecaoEntrega entrega={e} trabalhoId={trabalhoId} />
          </div>
        </div>
      ))}
    </div>
  )
}

function TrabalhoItem({ trabalho }) {
  const [aberto, setAberto] = useState(false)
  return (
    <Card>
      <CardContent>
        <button
          type="button"
          onClick={() => setAberto((v) => !v)}
          className="flex w-full items-center justify-between text-left"
        >
          <div>
            <p className="font-medium">{trabalho.titulo}</p>
            <p className="text-xs text-muted-foreground">
              Prazo: {formatarData(trabalho.prazo_entrega, true)}
            </p>
          </div>
          {aberto ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
        </button>
        {aberto && (
          <div className="mt-4 border-t pt-4">
            <EntregasList trabalhoId={trabalho.id} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default function AbaTrabalhos({ turmaId }) {
  const { data, isLoading, isError, refetch } = useTurmaTrabalhos(turmaId)
  if (isLoading) return <Spinner />
  if (isError) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <EmptyState message="Nenhum trabalho cadastrado nesta turma." />

  return (
    <div className="space-y-3">
      {data.map((t) => (
        <TrabalhoItem key={t.id} trabalho={t} />
      ))}
    </div>
  )
}
