import { Link } from 'react-router-dom'
import { Clock, ArrowRight, GraduationCap } from 'lucide-react'
import { Card, CardContent, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { tipoLabel, cargaHorariaLabel } from '@/lib/format'

export default function CursoCard({ curso, mostrarVagas }) {
  const temVagas = curso.tem_vagas_disponiveis

  return (
    <Card className="flex flex-col overflow-hidden pt-0 transition-shadow hover:shadow-md">
      <div className="relative h-44 w-full overflow-hidden bg-muted">
        {curso.imagem ? (
          <img
            src={curso.imagem}
            alt={curso.nome}
            className="h-full w-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-muted-foreground">
            <GraduationCap className="h-10 w-10" />
          </div>
        )}
        <Badge className="absolute left-3 top-3" variant="secondary">
          {tipoLabel(curso.tipo)}
        </Badge>
      </div>

      <CardContent className="flex-1">
        <h3 className="line-clamp-2 text-lg font-semibold">{curso.nome}</h3>
        {curso.descricao_resumida && (
          <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">
            {curso.descricao_resumida}
          </p>
        )}
        <div className="mt-3 flex items-center gap-2 text-sm text-muted-foreground">
          <Clock className="h-4 w-4" />
          {cargaHorariaLabel(curso.carga_horaria)}
        </div>
        {mostrarVagas && (
          <div className="mt-3">
            <Badge variant={temVagas ? 'default' : 'outline'}>
              {temVagas ? 'Vagas disponíveis' : 'Vagas esgotadas'}
            </Badge>
          </div>
        )}
      </CardContent>

      <CardFooter>
        <Button asChild variant="outline" className="w-full">
          <Link to={`/cursos/${curso.id}`}>
            Saiba mais <ArrowRight className="ml-1 h-4 w-4" />
          </Link>
        </Button>
      </CardFooter>
    </Card>
  )
}
