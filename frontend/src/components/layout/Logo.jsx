import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'
import logoDark from '@/assets/ftz-logo-dark.svg' // texto branco — para fundos escuros
import logoLight from '@/assets/ftz-logo-light.svg' // texto preto — para fundos claros

// `light` = true quando o logo está sobre fundo escuro (ex.: hero transparente),
// exibindo a versão de texto branco; caso contrário, a versão de texto preto.
export default function Logo({ className, light }) {
  return (
    <Link to="/" aria-label="Faculdade de Teologia Zait" className="inline-flex items-center">
      <img
        src={light ? logoDark : logoLight}
        alt="Faculdade de Teologia Zait"
        className={cn('h-9 w-auto', className)}
      />
    </Link>
  )
}
