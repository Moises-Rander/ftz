import { useQuery, useMutation } from '@tanstack/react-query'
import {
  listarEdicoes,
  obterEdicao,
  inscrever,
  consultarStatus,
} from '@/services/vestibular'

export const useEdicoes = () =>
  useQuery({ queryKey: ['vestibular', 'edicoes'], queryFn: listarEdicoes })

export const useEdicao = (id) =>
  useQuery({
    queryKey: ['vestibular', 'edicao', id],
    queryFn: () => obterEdicao(id),
    enabled: !!id,
    retry: false, // 404 (edição inexistente) não deve reintentar
  })

export const useInscrever = (id) =>
  useMutation({ mutationFn: (payload) => inscrever(id, payload) })

export const useConsultarStatus = (id) =>
  useMutation({ mutationFn: (cpf) => consultarStatus(id, cpf) })
