import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

const VAZIO = { nome: '', email: '', telefone: '', assunto: '', mensagem: '' }

export default function LeadForm({ full = false }) {
  const [form, setForm] = useState(VAZIO)
  const [enviando, setEnviando] = useState(false)

  const onChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }))

  const onSubmit = (e) => {
    e.preventDefault()
    if (!form.nome || !form.email) {
      toast.error('Informe ao menos nome e email.')
      return
    }
    // Ainda não há endpoint de backend — simula o envio (será conectado depois).
    setEnviando(true)
    setTimeout(() => {
      setEnviando(false)
      setForm(VAZIO)
      toast.success('Mensagem enviada! Entraremos em contato em breve.')
    }, 500)
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="nome">Nome *</Label>
          <Input id="nome" name="nome" value={form.nome} onChange={onChange} placeholder="Seu nome" />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="email">Email *</Label>
          <Input id="email" name="email" type="email" value={form.email} onChange={onChange} placeholder="voce@email.com" />
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="telefone">Telefone</Label>
          <Input id="telefone" name="telefone" value={form.telefone} onChange={onChange} placeholder="(00) 00000-0000" />
        </div>
        {full && (
          <div className="space-y-1.5">
            <Label htmlFor="assunto">Assunto</Label>
            <Input id="assunto" name="assunto" value={form.assunto} onChange={onChange} placeholder="Assunto" />
          </div>
        )}
      </div>
      <div className="space-y-1.5">
        <Label htmlFor="mensagem">Mensagem{full ? '' : ' (opcional)'}</Label>
        <Textarea
          id="mensagem"
          name="mensagem"
          value={form.mensagem}
          onChange={onChange}
          rows={full ? 6 : 4}
          placeholder="Como podemos ajudar?"
        />
      </div>
      <Button type="submit" disabled={enviando} className="w-full sm:w-auto">
        {enviando ? 'Enviando...' : 'Enviar mensagem'}
      </Button>
    </form>
  )
}
