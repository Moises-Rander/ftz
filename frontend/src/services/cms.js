import api from '@/lib/api'

export const listarPosts = async ({ categoria } = {}) => {
  const params = {}
  if (categoria && categoria !== 'TODAS') params.categoria = categoria
  const { data } = await api.get('/cms/posts/', { params })
  return data
}

export const obterPost = async (slug) => {
  const { data } = await api.get(`/cms/posts/${slug}/`)
  return data
}

export const listarConteudo = async (secao) => {
  const params = secao ? { secao } : {}
  const { data } = await api.get('/cms/conteudo/', { params })
  return data
}

export const listarEquipe = async () => {
  const { data } = await api.get('/cms/equipe/')
  return data
}

export const listarDepoimentos = async () => {
  const { data } = await api.get('/cms/depoimentos/')
  return data
}
