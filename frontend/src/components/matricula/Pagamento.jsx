import { useState } from 'react'
import { Check, AlertTriangle, Tag } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { formatarBRL } from '@/lib/format'
import { METODOS_PAGAMENTO } from '@/lib/matricula'

export default function Pagamento({ turma, onConfirmar, enviando, erro, onVoltar }) {
  const [metodo, setMetodo] = useState('PIX')
  const [cupomInput, setCupomInput] = useState('')
  const [cupomAplicado, setCupomAplicado] = useState('')

  const precoBase = Number(turma.preco_base || 0)
  const descontoPromo = turma.promocao ? Number(turma.promocao.desconto || 0) : 0
  const valorPreview = Math.max(precoBase - descontoPromo, 0)

  const aplicarCupom = () => {
    setCupomAplicado(cupomInput.trim().toUpperCase())
  }

  const confirmar = () => {
    onConfirmar({ metodo_pagamento: metodo, codigo_cupom: cupomAplicado })
  }

  const erroCupom = erro?.tipo === 'cupom' ? erro.mensagem : null
  const erroGeral = erro && erro.tipo !== 'cupom' ? erro.mensagem : null

  return (
    <Card>
      <CardContent className="space-y-6">
        <h2 className="text-xl font-semibold">Pagamento</h2>

        {/* Resumo de valores */}
        <div className="rounded-lg border p-4 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Preço base</span>
            <span>{formatarBRL(precoBase)}</span>
          </div>
          {descontoPromo > 0 && (
            <div className="mt-2 flex justify-between text-green-700">
              <span>Promoção</span>
              <span>− {formatarBRL(descontoPromo)}</span>
            </div>
          )}
          <div className="mt-3 flex justify-between border-t pt-3 text-base font-semibold">
            <span>Valor {cupomAplicado ? 'parcial' : 'final'}</span>
            <span>{formatarBRL(valorPreview)}</span>
          </div>
          {cupomAplicado && (
            <p className="mt-1 text-xs text-muted-foreground">
              O desconto do cupom será aplicado no envio.
            </p>
          )}
        </div>

        {/* Cupom */}
        <div>
          <label className="mb-1.5 block text-sm font-medium">Cupom de desconto (opcional)</label>
          <div className="flex gap-2">
            <Input
              value={cupomInput}
              onChange={(e) => setCupomInput(e.target.value)}
              placeholder="Digite o código"
              className="uppercase"
            />
            <Button type="button" variant="outline" onClick={aplicarCupom} disabled={!cupomInput.trim()}>
              Aplicar
            </Button>
          </div>
          {cupomAplicado && !erroCupom && (
            <p className="mt-2 flex items-center gap-1 text-sm text-primary">
              <Tag className="h-4 w-4" /> Cupom <strong>{cupomAplicado}</strong> será aplicado no envio.
            </p>
          )}
          {erroCupom && <p className="mt-2 text-sm text-destructive">{erroCupom}</p>}
        </div>

        {/* Método de pagamento */}
        <div>
          <p className="mb-2 text-sm font-medium">Forma de pagamento</p>
          <div className="grid gap-3 sm:grid-cols-3">
            {METODOS_PAGAMENTO.map((m) => {
              const ativo = metodo === m.value
              return (
                <button
                  key={m.value}
                  type="button"
                  onClick={() => setMetodo(m.value)}
                  className={cn(
                    'relative flex flex-col items-start gap-1 rounded-lg border p-4 text-left transition',
                    ativo ? 'border-primary ring-2 ring-primary/30' : 'hover:border-primary/50'
                  )}
                >
                  {ativo && <Check className="absolute right-3 top-3 h-4 w-4 text-primary" />}
                  <m.icon className="h-6 w-6 text-primary" />
                  <span className="font-medium">{m.label}</span>
                  <span className="text-xs text-muted-foreground">{m.descricao}</span>
                </button>
              )
            })}
          </div>
        </div>

        {erroGeral && (
          <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
            <p>{erroGeral}</p>
          </div>
        )}

        <div className="flex gap-3">
          {onVoltar && (
            <Button type="button" variant="outline" onClick={onVoltar} disabled={enviando}>
              Voltar
            </Button>
          )}
          <Button onClick={confirmar} disabled={enviando}>
            {enviando ? 'Processando...' : 'Confirmar matrícula'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
