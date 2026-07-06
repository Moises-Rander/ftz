import { QrCode, Barcode, CreditCard } from 'lucide-react'

export const METODOS_PAGAMENTO = [
  { value: 'PIX', label: 'PIX', descricao: 'Aprovação imediata', icon: QrCode },
  { value: 'BOLETO', label: 'Boleto Bancário', descricao: 'Até 3 dias úteis', icon: Barcode },
  { value: 'CARTAO', label: 'Cartão de Crédito', descricao: 'Checkout seguro', icon: CreditCard },
]

const LABEL_DOC = {
  RG: 'RG (frente e verso)',
  CPF: 'CPF',
  HISTORICO_EM: 'Histórico do Ensino Médio',
}

export function documentosExigidos(cursoTipo) {
  const tipos = cursoTipo === 'GRADUACAO' ? ['RG', 'CPF', 'HISTORICO_EM'] : ['RG', 'CPF']
  return tipos.map((tipo) => ({ tipo, label: LABEL_DOC[tipo] }))
}

export const ETAPAS = [
  'Confirmar turma',
  'Dados pessoais',
  'Pagamento',
  'Instruções',
  'Documentos',
]
