import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, CalendarDays } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Spinner, ErrorState } from '@/components/common/StateComponents'
import { usePost } from '@/hooks/useCms'
import { formatarData } from '@/lib/format'

const container = 'mx-auto max-w-3xl px-4 sm:px-6 lg:px-8'

export default function BlogPost() {
  const { slug } = useParams()
  const { data: post, isLoading, isError } = usePost(slug)

  if (isLoading)
    return (
      <div className={`${container} py-16`}>
        <Spinner label="Carregando post..." />
      </div>
    )
  if (isError || !post)
    return (
      <div className={`${container} py-16`}>
        <ErrorState message="Post não encontrado." />
        <div className="mt-6 text-center">
          <Button asChild variant="outline">
            <Link to="/blog">
              <ArrowLeft className="mr-1 h-4 w-4" /> Voltar ao blog
            </Link>
          </Button>
        </div>
      </div>
    )

  return (
    <article className={`${container} py-12`}>
      <Button asChild variant="link" className="mb-4 px-0">
        <Link to="/blog">
          <ArrowLeft className="mr-1 h-4 w-4" /> Voltar ao blog
        </Link>
      </Button>

      {post.categoria && <Badge variant="secondary">{post.categoria}</Badge>}
      <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">{post.titulo}</h1>
      <p className="mt-3 flex items-center gap-1 text-sm text-muted-foreground">
        <CalendarDays className="h-4 w-4" /> {formatarData(post.data_publicacao)}
      </p>

      {post.imagem && (
        <img
          src={post.imagem}
          alt={post.titulo}
          className="mt-6 aspect-video w-full rounded-2xl object-cover"
        />
      )}

      <div className="mt-8 whitespace-pre-line text-base leading-relaxed text-foreground/90">
        {post.conteudo}
      </div>
    </article>
  )
}
