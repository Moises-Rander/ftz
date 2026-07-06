import { Outlet, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Navbar from './Navbar'
import Footer from './Footer'

export default function Layout() {
  const { pathname } = useLocation()

  // Sobe ao topo a cada troca de rota.
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])

  const isHome = pathname === '/'

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      {/* Home tem hero que fica sob a navbar transparente; demais páginas recebem espaço. */}
      <main className={isHome ? 'flex-1' : 'flex-1 pt-16'}>
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
