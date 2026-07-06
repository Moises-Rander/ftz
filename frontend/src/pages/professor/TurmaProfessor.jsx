import { Link, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Spinner, ErrorState } from '@/components/common/StateComponents'
import AbaAulas from '@/components/professor/AbaAulas'
import AbaAvaliacoes from '@/components/professor/AbaAvaliacoes'
import AbaTrabalhos from '@/components/professor/AbaTrabalhos'
import { useTurma } from '@/hooks/useCursos'
import { tipoLabel } from '@/lib/format'

export default function TurmaProfessor() {
  const { id } = useParams()
  const { data: turma, isLoading, isError, refetch } = useTurma(id)

  return (
    <div className="mx-auto max-w-5xl">
      <Button asChild variant="link" className="mb-2 px-0">
        <Link to="/portal-professor/dashboard">
          <ArrowLeft className="mr-1 h-4 w-4" /> Voltar
        </Link>
      </Button>

      {isLoading && <Spinner label="Carregando turma..." />}
      {isError && <ErrorState onRetry={refetch} />}

      {turma && (
        <>
          <div className="mb-6">
            <Badge variant="secondary">{tipoLabel(turma.curso_tipo)}</Badge>
            <h1 className="mt-2 text-2xl font-bold tracking-tight">{turma.curso_nome}</h1>
            <p className="text-muted-foreground">Turma {turma.nome || `#${turma.id}`}</p>
          </div>

          <Tabs defaultValue="aulas">
            <TabsList className="mb-6 flex w-full flex-wrap justify-start">
              <TabsTrigger value="aulas">Aulas</TabsTrigger>
              <TabsTrigger value="avaliacoes">Avaliações</TabsTrigger>
              <TabsTrigger value="trabalhos">Trabalhos</TabsTrigger>
            </TabsList>
            <TabsContent value="aulas">
              <AbaAulas turmaId={id} />
            </TabsContent>
            <TabsContent value="avaliacoes">
              <AbaAvaliacoes turmaId={id} />
            </TabsContent>
            <TabsContent value="trabalhos">
              <AbaTrabalhos turmaId={id} />
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  )
}
