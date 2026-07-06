import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Check, X, ClipboardCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Spinner, ErrorState } from '@/components/common/StateComponents'
import { cn } from '@/lib/utils'
import { useTurmaAlunos, useFrequenciaAula, useSalvarFrequencia } from '@/hooks/useProfessor'

export default function PainelFrequencia({ aula, turmaId }) {
  const [aberto, setAberto] = useState(false)
  const [presencas, setPresencas] = useState({})
  const [confirmando, setConfirmando] = useState(false)

  const alunos = useTurmaAlunos(turmaId)
  const freq = useFrequenciaAula(aula.id, aberto && aula.frequencia_lancada)
  const salvar = useSalvarFrequencia(aula.id)
  const qc = useQueryClient()

  // Inicializa toggles (padrão: ausente) e prefill se já lançada.
  useEffect(() => {
    if (!aberto || !alunos.data) return
    const base = {}
    alunos.data.forEach((a) => {
      base[a.id] = false
    })
    if (aula.frequencia_lancada && freq.data) {
      freq.data.forEach((f) => {
        base[f.aluno] = f.presente
      })
    }
    setPresencas(base)
    setConfirmando(false)
  }, [aberto, alunos.data, freq.data, aula.frequencia_lancada])

  const total = alunos.data?.length || 0
  const presentes = Object.values(presencas).filter(Boolean).length

  const enviar = () => {
    const itens = Object.entries(presencas).map(([aluno, presente]) => ({
      aluno: Number(aluno),
      presente,
    }))
    salvar.mutate(itens, {
      onSuccess: () => {
        toast.success('Frequência lançada com sucesso.')
        qc.invalidateQueries({ queryKey: ['prof-aulas', turmaId] })
        qc.invalidateQueries({ queryKey: ['prof-frequencia', aula.id] })
        setAberto(false)
      },
      onError: () => toast.error('Falha ao lançar frequência. Nenhum registro foi salvo.'),
    })
  }

  const carregando = alunos.isLoading || (aula.frequencia_lancada && freq.isLoading)

  return (
    <Dialog open={aberto} onOpenChange={setAberto}>
      <DialogTrigger asChild>
        <Button size="sm" variant={aula.frequencia_lancada ? 'outline' : 'default'}>
          <ClipboardCheck className="mr-1 h-4 w-4" />
          {aula.frequencia_lancada ? 'Editar frequência' : 'Lançar frequência'}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[85vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle>Frequência</DialogTitle>
        </DialogHeader>

        {carregando && <Spinner />}
        {alunos.isError && <ErrorState onRetry={alunos.refetch} />}

        {alunos.data && !carregando && (
          <>
            {total === 0 ? (
              <p className="py-6 text-center text-sm text-muted-foreground">
                Nenhum aluno matriculado nesta turma.
              </p>
            ) : (
              <>
                <p className="text-sm text-muted-foreground">
                  {presentes} de {total} presente(s). Toque para alternar.
                </p>
                <div className="max-h-[45vh] space-y-1 overflow-y-auto pr-1">
                  {alunos.data.map((a) => {
                    const presente = presencas[a.id]
                    return (
                      <button
                        key={a.id}
                        type="button"
                        onClick={() => setPresencas((p) => ({ ...p, [a.id]: !p[a.id] }))}
                        className="flex w-full items-center justify-between rounded-md border px-3 py-2 text-left text-sm hover:bg-accent"
                      >
                        <span>{a.nome}</span>
                        <span
                          className={cn(
                            'flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
                            presente
                              ? 'bg-green-600/10 text-green-700'
                              : 'bg-destructive/10 text-destructive'
                          )}
                        >
                          {presente ? <Check className="h-3.5 w-3.5" /> : <X className="h-3.5 w-3.5" />}
                          {presente ? 'Presente' : 'Ausente'}
                        </span>
                      </button>
                    )
                  })}
                </div>

                {confirmando ? (
                  <div className="rounded-lg border bg-muted/50 p-3">
                    <p className="text-sm">
                      Confirmar lançamento de frequência para <strong>{total}</strong> aluno(s)?
                    </p>
                    <div className="mt-3 flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => setConfirmando(false)} disabled={salvar.isPending}>
                        Cancelar
                      </Button>
                      <Button size="sm" onClick={enviar} disabled={salvar.isPending}>
                        {salvar.isPending ? 'Salvando...' : 'Confirmar'}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <Button onClick={() => setConfirmando(true)}>Salvar frequência</Button>
                )}
              </>
            )}
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
