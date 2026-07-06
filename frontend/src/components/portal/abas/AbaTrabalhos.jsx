import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { FileText, Upload, Download } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Spinner, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useTrabalhos, useEntregarTrabalho } from '@/hooks/useAluno'
import { formatarData } from '@/lib/format'

function statusInfo(t) {
  if (t.status_entrega === 'CORRIGIDO') return { label: 'Corrigido', variant: 'default' }
  if (t.status_entrega === 'ENTREGUE')
    return t.entregue_em_atraso
      ? { label: 'Entregue com atraso', variant: 'outline' }
      : { label: 'Entregue', variant: 'outline' }
  return { label: 'Pendente', variant: 'secondary' }
}

function ModalEntrega({ trabalho, turmaId }) {
  const [aberto, setAberto] = useState(false)
  const [arquivo, setArquivo] = useState(null)
  const entrega = useEntregarTrabalho()
  const queryClient = useQueryClient()
  const reenvio = trabalho.status_entrega === 'ENTREGUE'

  const enviar = () => {
    if (!arquivo) {
      toast.error('Selecione um arquivo.')
      return
    }
    entrega.mutate(
      { trabalhoId: trabalho.id, arquivo },
      {
        onSuccess: () => {
          toast.success('Trabalho enviado com sucesso.')
          queryClient.invalidateQueries({ queryKey: ['trabalhos-aluno', turmaId] })
          queryClient.invalidateQueries({ queryKey: ['boletim', turmaId] })
          setAberto(false)
          setArquivo(null)
        },
        onError: () => toast.error('Não foi possível enviar. Tente novamente.'),
      }
    )
  }

  return (
    <Dialog open={aberto} onOpenChange={setAberto}>
      <DialogTrigger asChild>
        <Button size="sm" variant={reenvio ? 'outline' : 'default'}>
          <Upload className="mr-1 h-4 w-4" /> {reenvio ? 'Reenviar' : 'Entregar'}
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{reenvio ? 'Reenviar trabalho' : 'Entregar trabalho'}</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">{trabalho.titulo}</p>
          <Input
            type="file"
            accept="image/*,application/pdf,.doc,.docx"
            onChange={(e) => setArquivo(e.target.files?.[0] || null)}
          />
          {arquivo && <p className="truncate text-xs text-muted-foreground">{arquivo.name}</p>}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setAberto(false)}>
            Cancelar
          </Button>
          <Button onClick={enviar} disabled={entrega.isPending}>
            {entrega.isPending ? 'Enviando...' : 'Enviar'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default function AbaTrabalhos({ turmaId }) {
  const { data, isLoading, isError, refetch } = useTrabalhos(turmaId)
  if (isLoading) return <Spinner />
  if (isError || !data) return <ErrorState onRetry={refetch} />
  if (data.length === 0) return <EmptyState message="Nenhum trabalho cadastrado ainda." />

  return (
    <div className="space-y-4">
      {data.map((t) => {
        const st = statusInfo(t)
        const corrigido = t.status_entrega === 'CORRIGIDO'
        return (
          <Card key={t.id}>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{t.titulo}</h3>
                    <Badge variant={st.variant}>{st.label}</Badge>
                  </div>
                  {t.descricao && <p className="mt-1 text-sm text-muted-foreground">{t.descricao}</p>}
                  <p className="mt-1 text-xs text-muted-foreground">
                    Prazo: {formatarData(t.prazo_entrega, true)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {t.arquivo_enunciado && (
                    <Button asChild size="sm" variant="ghost">
                      <a href={t.arquivo_enunciado} target="_blank" rel="noreferrer">
                        <Download className="mr-1 h-4 w-4" /> Enunciado
                      </a>
                    </Button>
                  )}
                  {!corrigido && <ModalEntrega trabalho={t} turmaId={turmaId} />}
                </div>
              </div>

              {corrigido && (
                <div className="rounded-lg bg-muted/60 p-3 text-sm">
                  <p className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-primary" /> Nota:{' '}
                    <strong>{t.nota ?? '—'}</strong>
                  </p>
                  {t.feedback && (
                    <p className="mt-1 text-muted-foreground">
                      <strong>Feedback:</strong> {t.feedback}
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
