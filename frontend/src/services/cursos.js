import api from '@/lib/api'

export const listarCursos = async ({ tipo, search } = {}) => {
  const params = {}
  if (tipo && tipo !== 'TODOS') params.tipo = tipo
  if (search) params.search = search
  const { data } = await api.get('/cursos/', { params })
  return data
}

export const obterCurso = async (id) => {
  const { data } = await api.get(`/cursos/${id}/`)
  return data
}

export const listarTurmasDoCurso = async (id) => {
  const { data } = await api.get(`/cursos/${id}/turmas/`)
  return data
}

export const obterTurma = async (id) => {
  const { data } = await api.get(`/turmas/${id}/`)
  return data
}

export const listarProfessoresDaTurma = async (id) => {
  const { data } = await api.get(`/turmas/${id}/professores/`)
  return data
}
