import { useState } from 'react'
import { CalendarDays } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner, ErrorState, EmptyState } from '@/components/common/StateComponents'
import { useTurmaAvaliacoes, useTurmaAlunos, useResultadosAvaliacao } from '@/hooks/useProfessor'
import { formatarData } from '@/lib/format'
import PainelResultados from './PainelResultados'

function IndicadorLancamento({ avaliacaoId, totalAlunos }) {
  const { data } = useResultadosAvaliacao(avaliacaoId, true)
  if (!data) return <Badge variant="secondary">—</Badge>
  const lancados = data.length
  if (lancados === 0) return <Badge variant="secondary">Pendente</Badge>
  if (totalAlunos && lancados >= totalAlunos)
    return <Badge className="border-green-600/40 text-green-700" variant="outline">Lançados</Badge>
  return <Badge variant="outline">Parcial ({lancados})</Badge>
}

function AvaliacaoRow({ avaliacao, turmaId, totalAlunos }) {
  const [aberto, setAberto] = useState(false)
  return (
    <Card>
      <CardContent className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="font-medium">{avaliacao.titulo}</p>
          <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
            <span className="flex items-center gap-1">
              <CalendarDays className="h-4 w-4" /> {formatarData(avaliacao.data)}
            </span>
            <span>Nota máxima: {avaliacao.nota_maxima}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <IndicadorLancamento avaliacaoId={avaliacao.id} totalAlunos={totalAlunos} />
          <Button size="sm" variant="outline" onClick={() => setAberto(true)}>
            Lançar / editar notas
          </Button>
        </div>
      </CardContent>
      <PainelResultados
        avaliacao={avaliacao}
        turmaId={turmaId}
        aberto={aberto}
        onOpenChange={setAberto}
      />
    </Card>
  )
}

export default function AbaAvaliacoes({ turmaId }) {
  const { data, isLoading, isError, refetch } = useTurmaAvaliacoes(turmaId)
  const alunos = useTurmaAlunos(turmaId)

  if (isLoading) return <Spinner />
  if (isError) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <EmptyState message="Nenhuma avaliação cadastrada nesta turma." />

  return (
    <div className="space-y-3">
      {data.map((av) => (
        <AvaliacaoRow key={av.id} avaliacao={av} turmaId={turmaId} totalAlunos={alunos.data?.length} />
      ))}
    </div>
  )
}
