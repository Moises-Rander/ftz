import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { MailCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import AuthLayout from '@/components/auth/AuthLayout'
import { solicitarReset } from '@/services/auth'

export default function RecuperarSenha() {
  const [email, setEmail] = useState('')
  const [enviado, setEnviado] = useState(false)

  const mutation = useMutation({
    mutationFn: () => solicitarReset(email),
    // Resposta genérica independentemente do resultado (segurança).
    onSettled: () => setEnviado(true),
  })

  if (enviado) {
    return (
      <AuthLayout title="Verifique seu email">
        <div className="flex flex-col items-center gap-3 text-center">
          <MailCheck className="h-12 w-12 text-primary" />
          <p className="text-sm text-muted-foreground">
            Se houver uma conta associada a este email, enviaremos as instruções para redefinir a
            senha. Verifique também a caixa de spam.
          </p>
          <Button asChild variant="outline" className="mt-2">
            <Link to="/login">Voltar ao login</Link>
          </Button>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Recuperar senha" subtitle="Informe seu email para receber o link de redefinição.">
      <form
        onSubmit={(e) => {
          e.preventDefault()
          if (email) mutation.mutate()
        }}
        className="space-y-4"
        noValidate
      >
        <div className="space-y-1.5">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="voce@email.com" />
        </div>
        <Button type="submit" className="w-full" disabled={mutation.isPending || !email}>
          {mutation.isPending ? 'Enviando...' : 'Enviar link'}
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-muted-foreground">
        <Link to="/login" className="hover:text-primary">
          Voltar ao login
        </Link>
      </p>
    </AuthLayout>
  )
}
