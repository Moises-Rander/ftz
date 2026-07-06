import api from '@/lib/api'

export const minhasTurmas = async () => {
  const { data } = await api.get('/professor/turmas/')
  return data
}

export const turmaAlunos = async (turmaId) => {
  const { data } = await api.get(`/professor/turmas/${turmaId}/alunos/`)
  return data
}

// --- Aulas / Frequência ---
export const turmaAulas = async (turmaId) => {
  const { data } = await api.get(`/professor/turmas/${turmaId}/aulas/`)
  return data
}

export const getFrequencia = async (aulaId) => {
  const { data } = await api.get(`/professor/aulas/${aulaId}/frequencia/`)
  return data
}

export const salvarFrequencia = async (aulaId, itens) => {
  const { data } = await api.post(`/professor/aulas/${aulaId}/frequencia/`, { itens })
  return data
}

// --- Avaliações / Resultados ---
export const turmaAvaliacoes = async (turmaId) => {
  const { data } = await api.get('/professor/avaliacoes/', { params: { turma: turmaId } })
  return data
}

export const getResultados = async (avaliacaoId) => {
  const { data } = await api.get(`/professor/avaliacoes/${avaliacaoId}/resultados/`)
  return data
}

export const salvarResultados = async (avaliacaoId, itens) => {
  const { data } = await api.post(`/professor/avaliacoes/${avaliacaoId}/resultados/`, { itens })
  return data
}

// --- Trabalhos / Entregas ---
export const turmaTrabalhos = async (turmaId) => {
  const { data } = await api.get('/professor/trabalhos/', { params: { turma: turmaId } })
  return data
}

export const trabalhoEntregas = async (trabalhoId) => {
  const { data } = await api.get(`/professor/trabalhos/${trabalhoId}/entregas/`)
  return data
}

export const corrigirEntrega = async (entregaId, { nota, feedback }) => {
  const { data } = await api.patch(`/professor/entregas/${entregaId}/`, { nota, feedback })
  return data
}
