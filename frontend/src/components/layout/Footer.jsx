import { Link } from 'react-router-dom'
import { Mail, Phone, MessageCircle, AtSign, MapPin } from 'lucide-react'
import { NAV_LINKS } from '@/lib/navigation'
import { CONTATO, INSTITUICAO, whatsappLink } from '@/lib/config'
import Logo from './Logo'

export default function Footer() {
  return (
    <footer className="border-t bg-muted/40">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-12 sm:px-6 lg:grid-cols-4 lg:px-8">
        <div className="lg:col-span-2">
          <Logo />
          <p className="mt-4 max-w-md text-sm text-muted-foreground">
            {INSTITUICAO.descricao}
          </p>
          <div className="mt-4 flex gap-3">
            <a
              href={CONTATO.instagram}
              target="_blank"
              rel="noreferrer"
              aria-label="Instagram"
              className="flex h-9 w-9 items-center justify-center rounded-full border hover:bg-accent"
            >
              <AtSign className="h-4 w-4" />
            </a>
            <a
              href={whatsappLink()}
              target="_blank"
              rel="noreferrer"
              aria-label="WhatsApp"
              className="flex h-9 w-9 items-center justify-center rounded-full border hover:bg-accent"
            >
              <MessageCircle className="h-4 w-4" />
            </a>
          </div>
        </div>

        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide">Navegação</h3>
          <ul className="space-y-2 text-sm text-muted-foreground">
            {NAV_LINKS.map((link) => (
              <li key={link.to}>
                <Link to={link.to} className="hover:text-primary">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide">Contato</h3>
          <ul className="space-y-3 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <Mail className="mt-0.5 h-4 w-4 shrink-0" />
              <a href={`mailto:${CONTATO.email}`} className="hover:text-primary">
                {CONTATO.email}
              </a>
            </li>
            <li className="flex items-start gap-2">
              <Phone className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{CONTATO.telefone}</span>
            </li>
            <li className="flex items-start gap-2">
              <MessageCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <a href={whatsappLink()} target="_blank" rel="noreferrer" className="hover:text-primary">
                WhatsApp
              </a>
            </li>
            <li className="flex items-start gap-2">
              <MapPin className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{CONTATO.endereco}</span>
            </li>
          </ul>
        </div>
      </div>
      <div className="border-t py-4">
        <p className="text-center text-xs text-muted-foreground">
          © {new Date().getFullYear()} {INSTITUICAO.nome}. Todos os direitos reservados.
        </p>
      </div>
    </footer>
  )
}
