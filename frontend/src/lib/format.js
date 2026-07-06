export const tipoLabel = (tipo) =>
  ({ GRADUACAO: 'Graduação', FORMACAO: 'Formação' }[tipo] || tipo)

export const statusTurmaLabel = (status) =>
  ({ ABERTA: 'Aberta', FECHADA: 'Fechada', ENCERRADA: 'Encerrada' }[status] || status)

export const formatarData = (valor, comHora = false) => {
  if (!valor) return ''
  try {
    const d = new Date(valor)
    return d.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      ...(comHora ? { hour: '2-digit', minute: '2-digit' } : {}),
    })
  } catch {
    return valor
  }
}

export const cargaHorariaLabel = (horas) =>
  horas ? `${horas}h` : 'Carga horária a definir'

export const formatarBRL = (valor) => {
  const n = Number(valor)
  if (Number.isNaN(n)) return 'R$ 0,00'
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}
