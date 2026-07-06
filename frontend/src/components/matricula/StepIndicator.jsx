import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ETAPAS } from '@/lib/matricula'

// atual: índice 1-based da etapa corrente.
export default function StepIndicator({ atual }) {
  return (
    <ol className="flex items-center gap-2 overflow-x-auto pb-2">
      {ETAPAS.map((label, i) => {
        const n = i + 1
        const feito = n < atual
        const ativo = n === atual
        return (
          <li key={label} className="flex flex-1 items-center gap-2">
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  'flex h-8 w-8 shrink-0 items-center justify-center rounded-full border text-sm font-semibold',
                  feito && 'border-primary bg-primary text-primary-foreground',
                  ativo && 'border-primary text-primary',
                  !feito && !ativo && 'border-muted-foreground/30 text-muted-foreground'
                )}
              >
                {feito ? <Check className="h-4 w-4" /> : n}
              </span>
              <span
                className={cn(
                  'hidden whitespace-nowrap text-sm sm:inline',
                  ativo ? 'font-medium text-foreground' : 'text-muted-foreground'
                )}
              >
                {label}
              </span>
            </div>
            {n < ETAPAS.length && <div className="h-px flex-1 bg-border" />}
          </li>
        )
      })}
    </ol>
  )
}
