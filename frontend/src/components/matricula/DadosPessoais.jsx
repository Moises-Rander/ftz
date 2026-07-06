import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { maskCPF, maskTelefone, apenasDigitos, isEmailValido, isCpfValido } from '@/lib/masks'

export default function DadosPessoais({ valorInicial, onContinuar, onVoltar }) {
  const [form, setForm] = useState(
    valorInicial || { nome: '', email: '', cpf: '', telefone: '', data_nascimento: '' }
  )
  const [erros, setErros] = useState({})

  const onChange = (campo, valor) => {
    setForm((f) => ({ ...f, [campo]: valor }))
    setErros((e) => ({ ...e, [campo]: undefined }))
  }

  const validar = () => {
    const e = {}
    if (!form.nome.trim()) e.nome = 'Informe seu nome completo.'
    if (!isEmailValido(form.email)) e.email = 'Informe um email válido.'
    if (!isCpfValido(form.cpf)) e.cpf = 'CPF inválido.'
    if (apenasDigitos(form.telefone).length < 10) e.telefone = 'Telefone inválido.'
    if (!form.data_nascimento) e.data_nascimento = 'Informe a data de nascimento.'
    setErros(e)
    return Object.keys(e).length === 0
  }

  const submit = (ev) => {
    ev.preventDefault()
    if (validar()) onContinuar(form)
  }

  return (
    <Card>
      <CardContent>
        <h2 className="text-xl font-semibold">Seus dados</h2>
        <form onSubmit={submit} className="mt-5 space-y-4" noValidate>
          <div className="space-y-1.5">
            <Label htmlFor="nome">Nome completo *</Label>
            <Input id="nome" value={form.nome} onChange={(e) => onChange('nome', e.target.value)} />
            {erros.nome && <p className="text-xs text-destructive">{erros.nome}</p>}
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="email">Email *</Label>
            <Input id="email" type="email" value={form.email} onChange={(e) => onChange('email', e.target.value)} />
            {erros.email && <p className="text-xs text-destructive">{erros.email}</p>}
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="cpf">CPF *</Label>
              <Input id="cpf" inputMode="numeric" value={form.cpf}
                onChange={(e) => onChange('cpf', maskCPF(e.target.value))} placeholder="000.000.000-00" />
              {erros.cpf && <p className="text-xs text-destructive">{erros.cpf}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="telefone">Telefone *</Label>
              <Input id="telefone" inputMode="numeric" value={form.telefone}
                onChange={(e) => onChange('telefone', maskTelefone(e.target.value))} placeholder="(00) 00000-0000" />
              {erros.telefone && <p className="text-xs text-destructive">{erros.telefone}</p>}
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="nasc">Data de nascimento *</Label>
            <Input id="nasc" type="date" value={form.data_nascimento}
              onChange={(e) => onChange('data_nascimento', e.target.value)} className="sm:max-w-xs" />
            {erros.data_nascimento && <p className="text-xs text-destructive">{erros.data_nascimento}</p>}
          </div>

          <div className="flex gap-3">
            {onVoltar && (
              <Button type="button" variant="outline" onClick={onVoltar}>
                Voltar
              </Button>
            )}
            <Button type="submit">Continuar</Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
