import { Loader2, AlertTriangle, Inbox } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'

export function Spinner({ label = 'Carregando...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <span className="text-sm">{label}</span>
    </div>
  )
}

export function CardsSkeleton({ count = 3 }) {
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-xl border p-4">
          <Skeleton className="mb-4 h-40 w-full rounded-lg" />
          <Skeleton className="mb-2 h-5 w-3/4" />
          <Skeleton className="mb-2 h-4 w-1/2" />
          <Skeleton className="h-9 w-28" />
        </div>
      ))}
    </div>
  )
}

export function ErrorState({ message = 'Não foi possível carregar as informações. Tente novamente em instantes.', onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <AlertTriangle className="h-10 w-10 text-destructive" />
      <p className="max-w-md text-muted-foreground">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 rounded-md border px-4 py-2 text-sm font-medium hover:bg-accent"
        >
          Tentar novamente
        </button>
      )}
    </div>
  )
}

export function EmptyState({ message = 'Nada por aqui ainda.' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center text-muted-foreground">
      <Inbox className="h-10 w-10" />
      <p className="max-w-md">{message}</p>
    </div>
  )
}
