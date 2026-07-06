import { useState } from 'react'
import { toast } from 'sonner'
import {
  Clock,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Upload,
  FileCheck2,
  PartyPopper,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Spinner, ErrorState } from '@/components/common/StateComponents'
import { useStatusMatricula, useEnviarDocumentos } from '@/hooks/useMatricula'
import { documentosExigidos } from '@/lib/matricula'

function UploadDocumentos({ token, statusData, onEnviado }) {
  const exigidos = documentosExigidos(statusData.turma?.curso_tipo)
  const enviadosSet = new Set((statusData.documentos || []).map((d) => d.tipo))
  const [arquivos, setArquivos] = useState({})
  const envio = useEnviarDocumentos(token)

  const escolher = (tipo, file) => setArquivos((a) => ({ ...a, [tipo]: file }))

  const enviar = () => {
    if (Object.keys(arquivos).length === 0) {
      toast.error('Selecione ao menos um documento.')
      return
    }
    envio.mutate(arquivos, {
      onSuccess: () => {
        toast.success('Documento(s) enviado(s) com sucesso.')
        setArquivos({})
        onEnviado()
      },
      onError: () => toast.error('Não foi possível enviar. Tente novamente.'),
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3 rounded-lg border border-green-600/30 bg-green-600/5 p-4">
        <CheckCircle2 className="mt-0.5 h-6 w-6 shrink-0 text-green-600" />
        <div>
          <p className="font-semibold">Pagamento confirmado!</p>
          <p className="text-sm text-muted-foreground">
            Agora envie os documentos exigidos para concluir a matrícula.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {exigidos.map(({ tipo, label }) => {
          const enviado = enviadosSet.has(tipo)
          const selecionado = arquivos[tipo]
          return (
            <div key={tipo} className="flex flex-col gap-2 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-medium">{label}</p>
                {enviado ? (
                  <Badge variant="outline" className="mt-1 border-green-600/40 text-green-700">
                    <FileCheck2 className="mr-1 h-3.5 w-3.5" /> Enviado
                  </Badge>
                ) : (
                  <Badge variant="secondary" className="mt-1">Pendente</Badge>
                )}
              </div>
              <div className="sm:w-64">
                <Input
                  type="file"
                  accept="image/*,application/pdf"
                  onChange={(e) => escolher(tipo, e.target.files?.[0])}
                />
                {selecionado && (
                  <p className="mt-1 truncate text-xs text-muted-foreground">{selecionado.name}</p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <Button onClick={enviar} disabled={envio.isPending}>
        <Upload className="mr-2 h-4 w-4" />
        {envio.isPending ? 'Enviando...' : 'Enviar documentos'}
      </Button>

      <p className="text-sm text-muted-foreground">
        Você pode reenviar um documento para substituí-lo. Após o envio, nossa administração
        revisará os documentos e você receberá um email com o resultado da validação.
      </p>
    </div>
  )
}

export default function StatusDocumentos({ token }) {
  const { data, isLoading, isError, refetch, isFetching } = useStatusMatricula(token)

  if (isLoading)
    return <Spinner label="Consultando sua matrícula..." />

  if (isError || !data)
    return (
      <ErrorState message="Não localizamos uma matrícula com este token. Verifique o link recebido por email." />
    )

  const status = data.status

  return (
    <Card>
      <CardContent className="space-y-4">
        {status === 'AGUARDANDO_PAGAMENTO' && (
          <div className="space-y-4">
            <div className="flex items-start gap-3 rounded-lg border p-4">
              <Clock className="mt-0.5 h-6 w-6 shrink-0 text-amber-600" />
              <div>
                <p className="font-semibold">Pagamento ainda não confirmado</p>
                <p className="text-sm text-muted-foreground">
                  Assim que o pagamento for identificado, você poderá enviar os documentos.
                  A confirmação pode levar alguns minutos (ou até 3 dias úteis no boleto).
                </p>
              </div>
            </div>
            <Button variant="outline" onClick={() => refetch()} disabled={isFetching}>
              <RefreshCw className={`mr-2 h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
              Verificar novamente
            </Button>
          </div>
        )}

        {status === 'AGUARDANDO_VALIDACAO' && (
          <UploadDocumentos token={token} statusData={data} onEnviado={refetch} />
        )}

        {status === 'APROVADA' && (
          <div className="flex flex-col items-center gap-3 py-8 text-center">
            <PartyPopper className="h-12 w-12 text-primary" />
            <h2 className="text-2xl font-bold">Matrícula aprovada!</h2>
            <p className="max-w-md text-muted-foreground">
              Parabéns! Sua matrícula foi aprovada. Enviamos ao seu email as instruções para
              definir sua senha e acessar o Portal do Aluno.
            </p>
          </div>
        )}

        {status === 'REJEITADA' && (
          <div className="flex flex-col items-center gap-3 py-8 text-center">
            <XCircle className="h-12 w-12 text-destructive" />
            <h2 className="text-2xl font-bold">Matrícula não aprovada</h2>
            <p className="max-w-md text-muted-foreground">
              Infelizmente sua matrícula não pôde ser aprovada.
            </p>
            {data.motivo_rejeicao && (
              <p className="max-w-md rounded-lg bg-muted p-3 text-sm">
                <strong>Motivo:</strong> {data.motivo_rejeicao}
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
