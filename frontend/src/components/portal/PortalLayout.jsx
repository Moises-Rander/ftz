import { useState } from 'react'
import { NavLink, Outlet, useNavigate, Link } from 'react-router-dom'
import { LogOut, Menu } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger, SheetClose, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import Logo from '@/components/layout/Logo'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/useAuthStore'
import { logout as logoutService } from '@/services/auth'
import { NAV_ALUNO } from '@/lib/portalNav'

function NavItens({ items }) {
  return (
    <nav className="flex flex-col gap-1">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              isActive ? 'bg-primary text-primary-foreground' : 'text-foreground/70 hover:bg-accent'
            )
          }
        >
          <item.icon className="h-4 w-4" />
          {item.label}
        </NavLink>
      ))}
    </nav>
  )
}

export default function PortalLayout({ items = NAV_ALUNO }) {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const refresh = useAuthStore((s) => s.refresh)
  const logoutStore = useAuthStore((s) => s.logout)
  const [saindo, setSaindo] = useState(false)

  const sair = async () => {
    setSaindo(true)
    await logoutService(refresh)
    logoutStore()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen bg-muted/30">
      {/* Sidebar fixa (desktop) */}
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col border-r bg-background lg:flex">
        <div className="flex h-16 items-center border-b px-6">
          <Logo />
        </div>
        <div className="flex-1 p-4">
          <NavItens items={items} />
        </div>
      </aside>

      <div className="lg:pl-64">
        {/* Header */}
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-background px-4 sm:px-6">
          <div className="flex items-center gap-3">
            {/* Menu mobile */}
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="outline" size="icon" className="lg:hidden" aria-label="Menu">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-64 p-0">
                <SheetHeader className="h-16 justify-center border-b px-6">
                  <SheetTitle>
                    <Logo />
                  </SheetTitle>
                </SheetHeader>
                <div className="p-4">
                  <SheetClose asChild>
                    <div>
                      <NavItens items={items} />
                    </div>
                  </SheetClose>
                </div>
              </SheetContent>
            </Sheet>
            <span className="text-sm text-muted-foreground">
              Olá, <strong className="text-foreground">{user?.nome || 'Aluno'}</strong>
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Button asChild variant="ghost" size="sm" className="hidden sm:inline-flex">
              <Link to="/">Ver site</Link>
            </Button>
            <Button variant="outline" size="sm" onClick={sair} disabled={saindo}>
              <LogOut className="mr-1 h-4 w-4" />
              {saindo ? 'Saindo...' : 'Sair'}
            </Button>
          </div>
        </header>

        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
