import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from '@/components/ui/sonner'

import Layout from '@/components/layout/Layout'
import Home from '@/pages/Home'
import Cursos from '@/pages/Cursos'
import CursoDetalhe from '@/pages/CursoDetalhe'
import TurmaDetalhe from '@/pages/TurmaDetalhe'
import Vestibular from '@/pages/Vestibular'
import InscricaoVestibular from '@/pages/InscricaoVestibular'
import ResultadoVestibular from '@/pages/ResultadoVestibular'
import Sobre from '@/pages/Sobre'
import Blog from '@/pages/Blog'
import BlogPost from '@/pages/BlogPost'
import Contato from '@/pages/Contato'
import Matricula from '@/pages/Matricula'
import AcompanharMatricula from '@/pages/AcompanharMatricula'
import NotFound from '@/pages/NotFound'

import Login from '@/pages/auth/Login'
import RecuperarSenha from '@/pages/auth/RecuperarSenha'
import RedefinirSenha from '@/pages/auth/RedefinirSenha'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import PortalLayout from '@/components/portal/PortalLayout'
import { NAV_PROFESSOR } from '@/lib/portalNav'
import Dashboard from '@/pages/portal/Dashboard'
import MinhasTurmas from '@/pages/portal/MinhasTurmas'
import TurmaPortal from '@/pages/portal/TurmaPortal'
import Perfil from '@/pages/portal/Perfil'
import DashboardProfessor from '@/pages/professor/DashboardProfessor'
import MinhasTurmasProfessor from '@/pages/professor/MinhasTurmasProfessor'
import TurmaProfessor from '@/pages/professor/TurmaProfessor'
import PerfilProfessor from '@/pages/professor/PerfilProfessor'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60 * 5,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Site público */}
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/cursos" element={<Cursos />} />
            <Route path="/cursos/:id" element={<CursoDetalhe />} />
            <Route path="/turmas/:id" element={<TurmaDetalhe />} />
            <Route path="/vestibular" element={<Vestibular />} />
            <Route path="/vestibular/:id/inscrever" element={<InscricaoVestibular />} />
            <Route path="/vestibular/:id/resultado" element={<ResultadoVestibular />} />
            <Route path="/sobre" element={<Sobre />} />
            <Route path="/blog" element={<Blog />} />
            <Route path="/blog/:slug" element={<BlogPost />} />
            <Route path="/contato" element={<Contato />} />
            <Route path="/matricula/acompanhar" element={<AcompanharMatricula />} />
            <Route path="/matricula/:turmaId" element={<Matricula />} />
            <Route path="*" element={<NotFound />} />
          </Route>

          {/* Autenticação */}
          <Route path="/login" element={<Login />} />
          <Route path="/recuperar-senha" element={<RecuperarSenha />} />
          <Route path="/redefinir-senha" element={<RedefinirSenha />} />

          {/* Portal do Aluno (protegido) */}
          <Route
            path="/portal"
            element={
              <ProtectedRoute allowedRole="ALUNO">
                <PortalLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/portal/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="turmas" element={<MinhasTurmas />} />
            <Route path="turmas/:id" element={<TurmaPortal />} />
            <Route path="perfil" element={<Perfil />} />
          </Route>

          {/* Portal do Professor (protegido) */}
          <Route
            path="/portal-professor"
            element={
              <ProtectedRoute allowedRole="PROFESSOR">
                <PortalLayout items={NAV_PROFESSOR} />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/portal-professor/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardProfessor />} />
            <Route path="turmas" element={<MinhasTurmasProfessor />} />
            <Route path="turmas/:id" element={<TurmaProfessor />} />
            <Route path="perfil" element={<PerfilProfessor />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster richColors position="top-right" />
    </QueryClientProvider>
  )
}
