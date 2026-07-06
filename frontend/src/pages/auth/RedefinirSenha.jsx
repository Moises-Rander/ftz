import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { CheckCircle2, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import AuthLayout from '@/components/auth/AuthLayout'
import { confirmarReset } from '@/services/auth'

export default function RedefinirSenha() {
  const [params] = useSearchParams()
  const uid = params.get('uid') || ''
  const token = params.get('token') || ''

  const [senha, setSenha] = useState('')
  const [confirma, setConfirma] = useState('')
  const [erro, setErro] = useState('')

  const mutation = useMutation({
    mutationFn: () =>
      confirmarReset({ uid, token, new_password: senha, new_password_confirm: confirma }),
    onError: (err) => {
      const data = err?.response?.data
      const texto = JSON.stringify(data || '').toLowerCase()
      if (texto.includes('token') || texto.includes('link') || texto.includes('uid'))
        setErro('token')
      else if (data?.new_password)
        setErro(Array.isArray(data.new_password) ? data.new_password[0] : String(data.new_password))
      else setErro('generico')
    },
  })

  const linkInvalido = !uid || !token

  const onSubmit = (e) => {
    e.preventDefault()
    setErro('')
    if (senha.length < 8) {
      setErro('A senha deve ter ao menos 8 caracteres.')
      return
    }
    if (senha !== confirma) {
      setErro('As senhas não conferem.')
      return
    }
    mutation.mutate()
  }

  if (mutation.isSuccess) {
    return (
      <AuthLayout title="Senha definida!">
        <div className="flex flex-col items-center gap-3 text-center">
          <CheckCircle2 className="h-12 w-12 text-primary" />
          <p className="text-sm text-muted-foreground">
            Sua senha foi definida com sucesso. Agora você já pode acessar o Portal do Aluno.
          </p>
          <Button asChild className="mt-2">
            <Link to="/login">Ir para o login</Link>
          </Button>
        </div>
      </AuthLayout>
    )
  }

  if (linkInvalido || erro === 'token') {
    return (
      <AuthLayout title="Link inválido ou expirado">
        <div className="flex flex-col items-center gap-3 text-center">
          <AlertTriangle className="h-12 w-12 text-destructive" />
          <p className="text-sm text-muted-foreground">
            Este link de redefinição é inválido ou já expirou. Solicite um novo link para continuar.
          </p>
          <Button asChild variant="outline" className="mt-2">
            <Link to="/recuperar-senha">Solicitar novo link</Link>
          </Button>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Definir nova senha" subtitle="Crie uma senha para acessar o portal.">
      <form onSubmit={onSubmit} className="space-y-4" noValidate>
        <div className="space-y-1.5">
          <Label htmlFor="senha">Nova senha</Label>
          <Input id="senha" type="password" value={senha} onChange={(e) => setSenha(e.target.value)} placeholder="Mínimo 8 caracteres" />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="confirma">Confirmar senha</Label>
          <Input id="confirma" type="password" value={confirma} onChange={(e) => setConfirma(e.target.value)} />
        </div>
        {erro && erro !== 'token' && (
          <p className="text-sm text-destructive">
            {erro === 'generico' ? 'Não foi possível redefinir a senha. Tente novamente.' : erro}
          </p>
        )}
        <Button type="submit" className="w-full" disabled={mutation.isPending}>
          {mutation.isPending ? 'Salvando...' : 'Definir senha'}
        </Button>
      </form>
    </AuthLayout>
  )
}
