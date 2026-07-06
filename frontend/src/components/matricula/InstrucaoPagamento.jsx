import { ExternalLink, Info } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import CopyButton from './CopyButton'
import { formatarBRL } from '@/lib/format'

function Instrucao({ children }) {
  return (
    <div className="flex items-start gap-2 rounded-lg bg-muted/60 p-3 text-sm text-muted-foreground">
      <Info className="mt-0.5 h-4 w-4 shrink-0" />
      <p>{children}</p>
    </div>
  )
}

export default function InstrucaoPagamento({ info, onVerificarStatus }) {
  const metodo = info.metodo_pagamento

  return (
    <Card>
      <CardContent className="space-y-5">
        <div>
          <h2 className="text-xl font-semibold">Pagamento — {metodo}</h2>
          <p className="text-muted-foreground">
            Valor: <strong>{formatarBRL(info.valor_final)}</strong>
          </p>
        </div>

        {metodo === 'PIX' && (
          <div className="space-y-4">
            {info.pix_qrcode_base64 && (
              <img
                src={`data:image/png;base64,${info.pix_qrcode_base64}`}
                alt="QR Code PIX"
                className="mx-auto h-56 w-56 rounded-lg border bg-white p-2"
              />
            )}
            {info.pix_copia_cola && (
              <div>
                <p className="mb-1 text-sm font-medium">PIX copia e cola</p>
                <div className="flex items-center gap-2">
                  <code className="flex-1 truncate rounded bg-muted px-3 py-2 text-xs">
                    {info.pix_copia_cola}
                  </code>
                  <CopyButton value={info.pix_copia_cola} />
                </div>
              </div>
            )}
            <Instrucao>
              Após o pagamento, aguarde a confirmação — pode levar alguns minutos.
            </Instrucao>
            <Button onClick={onVerificarStatus}>Já paguei, verificar status</Button>
          </div>
        )}

        {metodo === 'BOLETO' && (
          <div className="space-y-4">
            {info.boleto_linha_digitavel && (
              <div>
                <p className="mb-1 text-sm font-medium">Linha digitável</p>
                <div className="flex items-center gap-2">
                  <code className="flex-1 truncate rounded bg-muted px-3 py-2 text-xs">
                    {info.boleto_linha_digitavel}
                  </code>
                  <CopyButton value={info.boleto_linha_digitavel} />
                </div>
              </div>
            )}
            {info.url_pagamento && (
              <Button asChild variant="outline">
                <a href={info.url_pagamento} target="_blank" rel="noreferrer">
                  <ExternalLink className="mr-2 h-4 w-4" /> Abrir boleto PDF
                </a>
              </Button>
            )}
            <Instrucao>
              O boleto pode levar até 3 dias úteis para ser compensado. Assim que o pagamento for
              confirmado, você poderá enviar os documentos.
            </Instrucao>
            <Button onClick={onVerificarStatus}>Verificar status</Button>
          </div>
        )}

        {metodo === 'CARTAO' && (
          <div className="space-y-4">
            {info.url_pagamento && (
              <Button asChild>
                <a href={info.url_pagamento} target="_blank" rel="noreferrer">
                  <ExternalLink className="mr-2 h-4 w-4" /> Finalizar pagamento
                </a>
              </Button>
            )}
            <Instrucao>
              Você será direcionado ao checkout seguro do Asaas em uma nova aba. Após concluir,
              volte aqui e verifique o status do pagamento.
            </Instrucao>
            <Button variant="outline" onClick={onVerificarStatus}>
              Verificar status do pagamento
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
