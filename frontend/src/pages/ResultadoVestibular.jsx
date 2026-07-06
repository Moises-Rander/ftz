import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  FileText,
  Clock,
  Search,
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Hourglass,
  Info,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner, ErrorState } from '@/components/common/StateComponents'
import { useEdicao, useConsultarStatus } from '@/hooks/useVestibular'
import { resultadoUrl } from '@/services/vestibular'
import { maskCPF, apenasDigitos, isCpfValido } from '@/lib/masks'

const container = 'mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8'

const STATUS_INFO = {
  INSCRITO: {
    icon: Info,
    cor: 'text-blue-600',
    msg: 'Sua inscrição está confirmada. Aguarde a divulgação do resultado.',
  },
  APROVADO: {
    icon: CheckCircle2,
    cor: 'text-green-600',
    msg: 'Parabéns! Você foi aprovado. Fique atento ao seu email com as instruções para realizar sua matrícula.',
  },
  REPROVADO: {
    icon: XCircle,
    cor: 'text-destructive',
    msg: 'Você não foi aprovado nesta edição. Fique de olho nas próximas edições do vestibular.',
  },
  LISTA_ESPERA: {
    icon: Hourglass,
    cor: 'text-amber-600',
    msg: 'Você está na lista de espera. Caso surja uma vaga, você será notificado por email.',
  },
  DESISTIU: {
    icon: Info,
    cor: 'text-muted-foreground',
    msg: 'Sua inscrição foi registrada como desistência.',
  },
}

function ConsultaStatus({ id }) {
  const [cpf, setCpf] = useState('')
  const [erro, setErro] = useState('')
  const consulta = useConsultarStatus(id)

  const onSubmit = (ev) => {
    ev.preventDefault()
    setErro('')
    if (!isCpfValido(cpf)) {
      setErro('Informe um CPF válido.')
      return
    }
    consulta.mutate(apenasDigitos(cpf))
  }

  const status = consulta.data?.status
  const info = status ? STATUS_INFO[status] : null
  const naoEncontrado = consulta.isError && consulta.error?.response?.status === 404

  return (
    <Card>
      <CardContent>
        <h2 className="flex items-center gap-2 text-lg font-semibold">
          <Search className="h-5 w-5 text-primary" /> Consultar minha inscrição
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Informe o CPF utilizado na inscrição para ver a sua situação.
        </p>

        <form onSubmit={onSubmit} className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end" noValidate>
          <div className="flex-1 space-y-1.5">
            <Label htmlFor="cpf">CPF</Label>
            <Input
              id="cpf"
              inputMode="numeric"
              value={cpf}
              onChange={(e) => {
                setCpf(maskCPF(e.target.value))
                setErro('')
              }}
              placeholder="000.000.000-00"
            />
          </div>
          <Button type="submit" disabled={consulta.isPending}>
            {consulta.isPending ? 'Consultando...' : 'Consultar'}
          </Button>
        </form>
        {erro && <p className="mt-2 text-xs text-destructive">{erro}</p>}

        {/* Resultado da consulta */}
        {info && (
          <div className="mt-5 flex items-start gap-3 rounded-lg border bg-muted/40 p-4">
            <info.icon className={`mt-0.5 h-6 w-6 shrink-0 ${info.cor}`} />
            <div>
              <p className="font-semibold">{consulta.data.status_display}</p>
              <p className="mt-1 text-sm text-muted-foreground">{info.msg}</p>
            </div>
          </div>
        )}
        {naoEncontrado && (
          <p className="mt-4 rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm">
            CPF não encontrado nesta edição. Verifique se você realizou a inscrição ou se o CPF
            está correto.
          </p>
        )}
        {consulta.isError && !naoEncontrado && (
          <p className="mt-4 rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm">
            Não foi possível consultar agora. Tente novamente em instantes.
          </p>
        )}
      </CardContent>
    </Card>
  )
}

export default function ResultadoVestibular() {
  const { id } = useParams()
  const { data: edicao, isLoading, isError } = useEdicao(id)

  if (isLoading)
    return (
      <div className={container}>
        <Spinner label="Carregando edição..." />
      </div>
    )

  if (isError || !edicao)
    return (
      <div className={container}>
        <ErrorState message="Edição do vestibular não encontrada." />
        <div className="mt-6 text-center">
          <Button asChild variant="outline">
            <Link to="/vestibular">
              <ArrowLeft className="mr-1 h-4 w-4" /> Voltar ao vestibular
            </Link>
          </Button>
        </div>
      </div>
    )

  return (
    <div className={container}>
      <Button asChild variant="link" className="mb-2 px-0">
        <Link to="/vestibular">
          <ArrowLeft className="mr-1 h-4 w-4" /> Voltar ao vestibular
        </Link>
      </Button>

      <h1 className="text-3xl font-bold tracking-tight">Resultado do Vestibular</h1>
      <p className="mt-2 text-muted-foreground">{edicao.curso_nome}</p>

      {/* Seção de resultado */}
      <Card className="mt-6">
        <CardContent>
          {edicao.resultado_publicado ? (
            <div className="flex flex-col items-start gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">Resultado disponível</h2>
                <p className="text-sm text-muted-foreground">
                  Baixe o PDF com a lista de aprovados.
                </p>
              </div>
              <Button asChild>
                <a href={resultadoUrl(edicao.id)} target="_blank" rel="noreferrer">
                  <FileText className="mr-2 h-4 w-4" /> Baixar resultado (PDF)
                </a>
              </Button>
            </div>
          ) : (
            <div className="flex items-start gap-3">
              <Clock className="mt-0.5 h-6 w-6 shrink-0 text-primary" />
              <div>
                <h2 className="text-lg font-semibold">Resultado ainda não divulgado</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  O resultado desta edição ainda não foi publicado. Acompanhe pelo nosso site e
                  pelas redes sociais da faculdade para ser avisado assim que sair.
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Seção de consulta de status */}
      <div className="mt-6">
        <ConsultaStatus id={id} />
      </div>
    </div>
  )
}
