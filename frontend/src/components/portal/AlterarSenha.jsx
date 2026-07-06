import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { useAlterarSenha } from '@/hooks/useAuth'

export default function AlterarSenha() {
  const alterar = useAlterarSenha()
  const [form, setForm] = useState({ old_password: '', new_password: '', new_password_confirm: '' })
  const [erro, setErro] = useState('')

  const salvar = (e) => {
    e.preventDefault()
    setErro('')
    if (form.new_password.length < 8) return setErro('A nova senha deve ter ao menos 8 caracteres.')
    if (form.new_password !== form.new_password_confirm) return setErro('As senhas não conferem.')
    alterar.mutate(form, {
      onSuccess: () => {
        toast.success('Senha alterada com sucesso.')
        setForm({ old_password: '', new_password: '', new_password_confirm: '' })
      },
      onError: (err) => {
        const data = err?.response?.data
        if (data?.old_password) setErro('Senha atual incorreta.')
        else setErro('Não foi possível alterar a senha.')
      },
    })
  }

  return (
    <Card>
      <CardContent>
        <h2 className="text-lg font-semibold">Alterar senha</h2>
        <form onSubmit={salvar} className="mt-5 space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="old">Senha atual</Label>
            <Input id="old" type="password" value={form.old_password} onChange={(e) => setForm((f) => ({ ...f, old_password: e.target.value }))} />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="new">Nova senha</Label>
              <Input id="new" type="password" value={form.new_password} onChange={(e) => setForm((f) => ({ ...f, new_password: e.target.value }))} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="new2">Confirmar nova senha</Label>
              <Input id="new2" type="password" value={form.new_password_confirm} onChange={(e) => setForm((f) => ({ ...f, new_password_confirm: e.target.value }))} />
            </div>
          </div>
          {erro && <p className="text-sm text-destructive">{erro}</p>}
          <Button type="submit" disabled={alterar.isPending}>
            {alterar.isPending ? 'Salvando...' : 'Alterar senha'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
