import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, PlayCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Spinner, ErrorState } from '@/components/common/StateComponents'
import StepIndicator from '@/components/matricula/StepIndicator'
import ConfirmarTurma from '@/components/matricula/ConfirmarTurma'
import DadosPessoais from '@/components/matricula/DadosPessoais'
import Pagamento from '@/components/matricula/Pagamento'
import InstrucaoPagamento from '@/components/matricula/InstrucaoPagamento'
import StatusDocumentos from '@/components/matricula/StatusDocumentos'
import { useTurma } from '@/hooks/useCursos'
import { useIniciarMatricula } from '@/hooks/useMatricula'
import { useMatriculaStore } from '@/stores/useMatriculaStore'
import { apenasDigitos } from '@/lib/masks'

const container = 'mx-auto max-w-2xl px-4 py-10 sm:px-6 lg:px-8'

function classificarErroMatricula(err) {
  const data = err?.response?.data
  const texto = JSON.stringify(data || '').toLowerCase()

  if (data?.codigo_cupom || texto.includes('cupom'))
    return { tipo: 'cupom', mensagem: 'Cupom inválido, expirado ou esgotado. Verifique o código ou remova-o.' }
  if (texto.includes('vestibular'))
    return { tipo: 'geral', mensagem: 'É necessário ter sido aprovado no vestibular desta turma para se matricular.' }
  if (texto.includes('prazo'))
    return { tipo: 'geral', mensagem: 'O prazo de matrícula após a aprovação no vestibular está encerrado.' }
  if (texto.includes('aprovada') && texto.includes('cpf'))
    return { tipo: 'geral', mensagem: 'Já existe uma matrícula aprovada para este CPF nesta turma.' }
  if (texto.includes('aberta') || texto.includes('vaga'))
    return { tipo: 'geral', mensagem: 'As vagas desta turma foram preenchidas. As matrículas estão encerradas.' }
  return { tipo: 'geral', mensagem: 'Não foi possível concluir a matrícula. Tente novamente em instantes.' }
}

export default function Matricula() {
  const { turmaId } = useParams()
  const { data: turma, isLoading, isError } = useTurma(turmaId)
  const iniciar = useIniciarMatricula()
  const { uploadToken, setUploadToken } = useMatriculaStore()

  const [step, setStep] = useState(1)
  const [dados, setDados] = useState(null)
  const [pagamentoInfo, setPagamentoInfo] = useState(null)
  const [erro, setErro] = useState(null)
  const [retomar, setRetomar] = useState(Boolean(uploadToken)) // matrícula anterior no sessionStorage

  if (isLoading)
    return (
      <div className={container}>
        <Spinner label="Carregando turma..." />
      </div>
    )
  if (isError || !turma)
    return (
      <div className={container}>
        <ErrorState message="Turma não encontrada." />
        <div className="mt-6 text-center">
          <Button asChild variant="outline">
            <Link to="/cursos">
              <ArrowLeft className="mr-1 h-4 w-4" /> Voltar aos cursos
            </Link>
          </Button>
        </div>
      </div>
    )

  const confirmarPagamento = ({ metodo_pagamento, codigo_cupom }) => {
    setErro(null)
    iniciar.mutate(
      {
        turma: Number(turmaId),
        nome: dados.nome.trim(),
        email: dados.email.trim(),
        cpf: apenasDigitos(dados.cpf),
        telefone: apenasDigitos(dados.telefone),
        data_nascimento: dados.data_nascimento,
        metodo_pagamento,
        codigo_cupom: codigo_cupom || '',
      },
      {
        onSuccess: (info) => {
          setUploadToken(info.upload_token)
          setPagamentoInfo(info)
          setStep(info.pagamento_necessario ? 4 : 5)
        },
        onError: (err) => setErro(classificarErroMatricula(err)),
      }
    )
  }

  return (
    <div className={container}>
      <Button asChild variant="link" className="mb-2 px-0">
        <Link to={`/turmas/${turmaId}`}>
          <ArrowLeft className="mr-1 h-4 w-4" /> Voltar à turma
        </Link>
      </Button>
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Matrícula</h1>

      {/* Banner de retomada (matrícula em andamento salva no navegador) */}
      {retomar && step === 1 && (
        <div className="mb-6 flex flex-col gap-3 rounded-lg border border-primary/30 bg-primary/5 p-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm">Você tem uma matrícula em andamento neste navegador.</p>
          <div className="flex gap-2">
            <Button size="sm" variant="ghost" onClick={() => setRetomar(false)}>
              Começar nova
            </Button>
            <Button size="sm" onClick={() => setStep(5)}>
              <PlayCircle className="mr-1 h-4 w-4" /> Continuar
            </Button>
          </div>
        </div>
      )}

      <div className="mb-8">
        <StepIndicator atual={step} />
      </div>

      {step === 1 && <ConfirmarTurma turma={turma} onContinuar={() => setStep(2)} />}

      {step === 2 && (
        <DadosPessoais
          valorInicial={dados}
          onContinuar={(d) => {
            setDados(d)
            setStep(3)
          }}
          onVoltar={() => setStep(1)}
        />
      )}

      {step === 3 && (
        <Pagamento
          turma={turma}
          onConfirmar={confirmarPagamento}
          enviando={iniciar.isPending}
          erro={erro}
          onVoltar={() => setStep(2)}
        />
      )}

      {step === 4 && pagamentoInfo && (
        <InstrucaoPagamento info={pagamentoInfo} onVerificarStatus={() => setStep(5)} />
      )}

      {step === 5 && <StatusDocumentos token={uploadToken} />}
    </div>
  )
}
