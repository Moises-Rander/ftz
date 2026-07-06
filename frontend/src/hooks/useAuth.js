import { useMutation, useQuery } from '@tanstack/react-query'
import { getMe, updateMe, alterarSenha } from '@/services/auth'

export const useMe = (enabled = true) =>
  useQuery({ queryKey: ['me'], queryFn: getMe, enabled })

export const useUpdateMe = () => useMutation({ mutationFn: updateMe })

export const useAlterarSenha = () => useMutation({ mutationFn: alterarSenha })
