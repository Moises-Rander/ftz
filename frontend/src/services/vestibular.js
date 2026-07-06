import api from '@/lib/api'
import { API_URL } from '@/lib/config'

export const listarEdicoes = async () => {
  const { data } = await api.get('/vestibular/edicoes/')
  return data
}

export const obterEdicao = async (id) => {
  const { data } = await api.get(`/vestibular/edicoes/${id}/`)
  return data
}

export const inscrever = async (id, payload) => {
  const { data } = await api.post(`/vestibular/edicoes/${id}/inscrever/`, payload)
  return data
}

export const consultarStatus = async (id, cpf) => {
  const { data } = await api.get(`/vestibular/edicoes/${id}/consultar-status/`, {
    params: { cpf },
  })
  return data
}

// URL direta para download do PDF de resultado (quando publicado).
export const resultadoUrl = (edicaoId) =>
  `${API_URL.replace(/\/$/, '')}/vestibular/edicoes/${edicaoId}/resultado/`
