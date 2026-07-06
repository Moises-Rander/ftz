import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { PenLine } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Spinner, ErrorState } from '@/components/common/StateComponents'
import { useTurmaAlunos, useResultadosAvaliacao, useSalvarResultados } from '@/hooks/useProfessor'

export default function PainelResultados({ avaliacao, turmaId, aberto, onOpenChange }) {
  const [notas, setNotas] = useState({})
  const [confirmando, setConfirmando] = useState(false)

  const alunos = useTurmaAlunos(turmaId)
  const resultados = useResultadosAvaliacao(avaliacao.id, aberto)
  const salvar = useSalvarResultados(avaliacao.id)
  const qc = useQueryClient()
  const notaMax = Number(avaliacao.nota_maxima)

  useEffect(() => {
    if (!aberto || !alunos.data) return
    const base = {}
    alunos.data.forEach((a) => {
      base[a.id] = ''
    })
    if (resultados.data) {
      resultados.data.forEach((r) => {
        base[r.aluno] = String(r.nota)
      })
    }
    setNotas(base)
    setConfirmando(false)
  }, [aberto, alunos.data, resultados.data])

  const preenchidas = Object.values(notas).filter((v) => v !== '' && v != null)

  const validar = () => {
    for (const [, valor] of Object.entries(notas)) {
      if (valor === '' || valor == null) continue
      const n = Number(valor)
      if (Number.isNaN(n) || n < 0 || n > notaMax) return false
    }
    return true
  }

  const enviar = () => {
    const itens = Object.entries(notas)
      .filter(([, v]) => v !== '' && v != null)
      .map(([aluno, nota]) => ({ aluno: Number(aluno), nota: Number(nota) }))
    salvar.mutate(itens, {
      onSuccess: () => {
        toast.success('Resultados lançados com sucesso.')
        qc.invalidateQueries({ queryKey: ['prof-resultados', avaliacao.id] })
        onOpenChange(false)
      },
      onError: () => toast.error('Falha ao lançar resultados. Nenhum registro foi salvo.'),
    })
  }

  const clicarSalvar = () => {
    if (!validar()) {
      toast.error(`Notas devem estar entre 0 e ${notaMax}.`)
      return
    }
    setConfirmando(true)
  }

  const carregando = alunos.isLoading || resultados.isLoading

  return (
    <Dialog open={aberto} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle>{avaliacao.titulo}</DialogTitle>
        </DialogHeader>

        {carregando && <Spinner />}
        {alunos.isError && <ErrorState onRetry={alunos.refetch} />}

        {alunos.data && !carregando && (
          <>
            <p className="text-sm text-muted-foreground">Nota máxima: {notaMax}</p>
            <div className="max-h-[45vh] space-y-2 overflow-y-auto pr-1">
              {alunos.data.map((a) => (
                <div key={a.id} className="flex items-center justify-between gap-3">
                  <span className="text-sm">{a.nome}</span>
                  <Input
                    type="number"
                    min="0"
                    max={notaMax}
                    step="0.1"
                    value={notas[a.id] ?? ''}
                    onChange={(e) => setNotas((n) => ({ ...n, [a.id]: e.target.value }))}
                    className="w-24"
                    placeholder="—"
                  />
                </div>
              ))}
            </div>

            {confirmando ? (
              <div className="rounded-lg border bg-muted/50 p-3">
                <p className="text-sm">
                  Confirmar lançamento de <strong>{preenchidas.length}</strong> nota(s)?
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
              <Button onClick={clicarSalvar}>
                <PenLine className="mr-1 h-4 w-4" /> Salvar resultados
              </Button>
            )}
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
