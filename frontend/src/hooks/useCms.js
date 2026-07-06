import { useQuery } from '@tanstack/react-query'
import {
  listarPosts,
  obterPost,
  listarConteudo,
  listarEquipe,
  listarDepoimentos,
} from '@/services/cms'

export const usePosts = (filtros = {}) =>
  useQuery({
    queryKey: ['posts', filtros],
    queryFn: () => listarPosts(filtros),
  })

export const usePost = (slug) =>
  useQuery({
    queryKey: ['post', slug],
    queryFn: () => obterPost(slug),
    enabled: !!slug,
  })

export const useConteudo = (secao) =>
  useQuery({
    queryKey: ['conteudo', secao || 'todos'],
    queryFn: () => listarConteudo(secao),
  })

export const useEquipe = () =>
  useQuery({ queryKey: ['equipe'], queryFn: listarEquipe })

export const useDepoimentos = () =>
  useQuery({ queryKey: ['depoimentos'], queryFn: listarDepoimentos })
