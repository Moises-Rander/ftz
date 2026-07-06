import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import AuthLayout from '@/components/auth/AuthLayout'
import { login as loginService } from '@/services/auth'
import { useAuthStore } from '@/stores/useAuthStore'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const loginStore = useAuthStore((s) => s.login)
  const destino = location.state?.from?.pathname || '/portal/dashboard'

  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')

  const mutation = useMutation({
    mutationFn: () => loginService(email, senha),
    onSuccess: (data) => {
      loginStore(data)
      navigate(destino, { replace: true })
    },
    onError: (err) => {
      const status = err?.response?.status
      setErro(
        status === 401
          ? 'Email ou senha inválidos, ou conta inativa.'
          : 'Não foi possível entrar. Tente novamente em instantes.'
      )
    },
  })

  const onSubmit = (e) => {
    e.preventDefault()
    setErro('')
    if (!email || !senha) {
      setErro('Informe email e senha.')
      return
    }
    mutation.mutate()
  }

  return (
    <AuthLayout title="Portal do Aluno" subtitle="Acesse com seu email e senha.">
      <form onSubmit={onSubmit} className="space-y-4" noValidate>
        <div className="space-y-1.5">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="voce@email.com" />
        </div>
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="senha">Senha</Label>
            <Link to="/recuperar-senha" className="text-xs text-primary hover:underline">
              Esqueci minha senha
            </Link>
          </div>
          <Input id="senha" type="password" value={senha} onChange={(e) => setSenha(e.target.value)} placeholder="••••••••" />
        </div>

        {erro && <p className="text-sm text-destructive">{erro}</p>}

        <Button type="submit" className="w-full" disabled={mutation.isPending}>
          {mutation.isPending ? 'Entrando...' : 'Entrar'}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-muted-foreground">
        <Link to="/" className="hover:text-primary">
          Voltar ao site
        </Link>
      </p>
    </AuthLayout>
  )
}
