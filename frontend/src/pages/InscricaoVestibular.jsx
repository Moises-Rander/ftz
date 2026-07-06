import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  CalendarDays,
  MapPin,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  Search,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner } from '@/components/common/StateComponents'
import { useEdicao, useInscrever } from '@/hooks/useVestibular'
import { maskCPF, maskTelefone, apenasDigitos, isEmailValido, isCpfValido } from '@/lib/masks'
import { formatarData } from '@/lib/format'

const container = 'mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8'
const VAZIO = { nome: '', email: '', cpf: '', telefone: '' }

function classificarErro(err) {
  const data = err?.response?.data
  const texto = JSON.stringify(data || '').toLowerCase()
  if (data?.cpf || texto.includes('cpf')) return 'cpf_duplicado'
  if (
    texto.includes('não estão abertas') ||
    texto.includes('nao estao abertas') ||
    texto.includes('vaga') ||
    texto.includes('encerrad')
  )
    return 'encerrada'
  return 'generico'
}

function Aviso({ icon: Icon, titulo, children }) {
  return (
    <div className={container}>
      <Card>
        <CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <Icon className="h-12 w-12 text-primary" />
          <h1 className="text-2xl font-bold">{titulo}</h1>
          <div className="max-w-md text-muted-foreground">{children}</div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function InscricaoVestibular() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { data: edicao, isLoading, isError } = useEdicao(id)
  const inscricao = useInscrever(id)

  const [form, setForm] = useState(VAZIO)
  const [erros, setErros] = useState({})
  const [sucesso, setSucesso] = useState(null)
  const [falha, setFalha] = useState(null)

  const inscricoesFechadas = edicao && !edicao.inscricoes_abertas
  const bloqueado = isError || inscricoesFechadas

  // Edição inexistente ou inscrições encerradas → redireciona para /vestibular.
  useEffect(() => {
    if (bloqueado) {
      const t = setTimeout(() => navigate('/vestibular'), 6000)
      return () => clearTimeout(t)
    }
  }, [bloqueado, navigate])

  if (isLoading)
    return (
      <div className={container}>
        <Spinner label="Carregando edição..." />
      </div>
    )

  if (isError)
    return (
      <Aviso icon={AlertTriangle} titulo="Edição não encontrada">
        Esta edição do vestibular não existe ou não está mais disponível. Você será
        redirecionado em instantes.
      </Aviso>
    )

  if (inscricoesFechadas)
    return (
      <Aviso icon={AlertTriangle} titulo="Inscrições encerradas">
        As inscrições para o vestibular de <strong>{edicao.curso_nome}</strong> estão
        encerradas. Você será redirecionado para a página do vestibular.
      </Aviso>
    )

  if (sucesso)
    return (
      <Aviso icon={CheckCircle2} titulo="Inscrição confirmada!">
        <p>
          Parabéns, <strong>{sucesso.nome}</strong>! Sua inscrição no vestibular de{' '}
          <strong>{edicao.curso_nome}</strong> foi registrada.
        </p>
        <div className="mt-4 rounded-lg bg-muted/60 p-4 text-left text-sm">
          <p className="flex items-center gap-2">
            <CalendarDays className="h-4 w-4" /> Prova: {formatarData(edicao.data_prova)}
          </p>
          <p className="mt-1 flex items-center gap-2">
            <MapPin className="h-4 w-4" /> {edicao.local_prova}
          </p>
        </div>
        <p className="mt-4">
          Enviamos um email de confirmação. Fique atento(a) à sua caixa de entrada para as
          próximas orientações.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Button asChild variant="outline">
            <Link to="/vestibular">Voltar ao vestibular</Link>
          </Button>
          <Button asChild>
            <Link to={`/vestibular/${id}/resultado`}>
              <Search className="mr-2 h-4 w-4" /> Consultar status
            </Link>
          </Button>
        </div>
      </Aviso>
    )

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
    setErros(e)
    return Object.keys(e).length === 0
  }

  const onSubmit = (ev) => {
    ev.preventDefault()
    setFalha(null)
    if (!validar()) return
    inscricao.mutate(
      {
        nome: form.nome.trim(),
        email: form.email.trim(),
        cpf: apenasDigitos(form.cpf),
        telefone: apenasDigitos(form.telefone),
      },
      {
        onSuccess: () => setSucesso({ nome: form.nome.trim() }),
        onError: (err) => setFalha(classificarErro(err)),
      }
    )
  }

  return (
    <div className={container}>
      <Button asChild variant="link" className="mb-2 px-0">
        <Link to="/vestibular">
          <ArrowLeft className="mr-1 h-4 w-4" /> Voltar ao vestibular
        </Link>
      </Button>

      <h1 className="text-3xl font-bold tracking-tight">Inscrição no Vestibular</h1>
      <div className="mt-3 rounded-lg border bg-muted/40 p-4 text-sm">
        <p className="text-base font-semibold">{edicao.curso_nome}</p>
        <div className="mt-2 flex flex-wrap gap-4 text-muted-foreground">
          <span className="flex items-center gap-1">
            <CalendarDays className="h-4 w-4" /> Prova: {formatarData(edicao.data_prova)}
          </span>
          <span className="flex items-center gap-1">
            <MapPin className="h-4 w-4" /> {edicao.local_prova}
          </span>
        </div>
      </div>

      {falha && (
        <div className="mt-6 rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm">
          {falha === 'cpf_duplicado' && (
            <p>
              Este CPF já possui inscrição nesta edição.{' '}
              <Link to={`/vestibular/${id}/resultado`} className="font-medium text-primary underline">
                Consultar status da inscrição
              </Link>
              .
            </p>
          )}
          {falha === 'encerrada' && (
            <p>As inscrições para esta edição foram encerradas.</p>
          )}
          {falha === 'generico' && (
            <p>Não foi possível concluir sua inscrição. Tente novamente em instantes.</p>
          )}
        </div>
      )}

      <form onSubmit={onSubmit} className="mt-6 space-y-4" noValidate>
        <div className="space-y-1.5">
          <Label htmlFor="nome">Nome completo *</Label>
          <Input
            id="nome"
            value={form.nome}
            onChange={(e) => onChange('nome', e.target.value)}
            placeholder="Seu nome completo"
          />
          {erros.nome && <p className="text-xs text-destructive">{erros.nome}</p>}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="email">Email *</Label>
          <Input
            id="email"
            type="email"
            value={form.email}
            onChange={(e) => onChange('email', e.target.value)}
            placeholder="voce@email.com"
          />
          {erros.email && <p className="text-xs text-destructive">{erros.email}</p>}
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-1.5">
            <Label htmlFor="cpf">CPF *</Label>
            <Input
              id="cpf"
              inputMode="numeric"
              value={form.cpf}
              onChange={(e) => onChange('cpf', maskCPF(e.target.value))}
              placeholder="000.000.000-00"
            />
            {erros.cpf && <p className="text-xs text-destructive">{erros.cpf}</p>}
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="telefone">Telefone *</Label>
            <Input
              id="telefone"
              inputMode="numeric"
              value={form.telefone}
              onChange={(e) => onChange('telefone', maskTelefone(e.target.value))}
              placeholder="(00) 00000-0000"
            />
            {erros.telefone && <p className="text-xs text-destructive">{erros.telefone}</p>}
          </div>
        </div>

        <Button type="submit" className="w-full sm:w-auto" disabled={inscricao.isPending}>
          {inscricao.isPending ? 'Enviando...' : 'Confirmar inscrição'}
        </Button>
      </form>
    </div>
  )
}
