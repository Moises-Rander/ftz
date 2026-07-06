import { Link, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Spinner, ErrorState } from '@/components/common/StateComponents'
import AbaGrade from '@/components/portal/abas/AbaGrade'
import AbaBoletim from '@/components/portal/abas/AbaBoletim'
import AbaFrequencia from '@/components/portal/abas/AbaFrequencia'
import AbaAvaliacoes from '@/components/portal/abas/AbaAvaliacoes'
import AbaTrabalhos from '@/components/portal/abas/AbaTrabalhos'
import { useTurma } from '@/hooks/useCursos'
import { tipoLabel } from '@/lib/format'

export default function TurmaPortal() {
  const { id } = useParams()
  const { data: turma, isLoading, isError, refetch } = useTurma(id)

  return (
    <div className="mx-auto max-w-5xl">
      <Button asChild variant="link" className="mb-2 px-0">
        <Link to="/portal/dashboard">
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

          <Tabs defaultValue="grade">
            <TabsList className="mb-6 flex w-full flex-wrap justify-start">
              <TabsTrigger value="grade">Grade / Horários</TabsTrigger>
              <TabsTrigger value="boletim">Boletim</TabsTrigger>
              <TabsTrigger value="frequencia">Frequência</TabsTrigger>
              <TabsTrigger value="avaliacoes">Avaliações</TabsTrigger>
              <TabsTrigger value="trabalhos">Trabalhos</TabsTrigger>
            </TabsList>

            <TabsContent value="grade">
              <AbaGrade turmaId={id} />
            </TabsContent>
            <TabsContent value="boletim">
              <AbaBoletim turmaId={id} />
            </TabsContent>
            <TabsContent value="frequencia">
              <AbaFrequencia turmaId={id} />
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
