import api from '@/lib/api'

export const listarMinhasMatriculas = async () => {
  const { data } = await api.get('/matriculas/')
  return data
}

export const gradeCompleta = async (turmaId) => {
  const { data } = await api.get(`/turmas/${turmaId}/grade-completa/`)
  return data
}

export const boletim = async (turmaId) => {
  const { data } = await api.get(`/aluno/turmas/${turmaId}/boletim/`)
  return data
}

export const frequencia = async (turmaId) => {
  const { data } = await api.get(`/aluno/turmas/${turmaId}/frequencia/`)
  return data
}

export const avaliacoes = async (turmaId) => {
  const { data } = await api.get(`/aluno/turmas/${turmaId}/avaliacoes/`)
  return data
}

export const trabalhos = async (turmaId) => {
  const { data } = await api.get(`/aluno/turmas/${turmaId}/trabalhos/`)
  return data
}

export const entregarTrabalho = async (trabalhoId, arquivo) => {
  const fd = new FormData()
  fd.append('arquivo', arquivo)
  const { data } = await api.post(`/aluno/trabalhos/${trabalhoId}/entregar/`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
