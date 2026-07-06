import { useMutation, useQuery } from '@tanstack/react-query'
import {
  iniciarMatricula,
  consultarStatusMatricula,
  enviarDocumentos,
} from '@/services/matriculas'

export const useIniciarMatricula = () =>
  useMutation({ mutationFn: iniciarMatricula })

// Consulta de status — sem polling automático; atualização manual via refetch.
export const useStatusMatricula = (token) =>
  useQuery({
    queryKey: ['matricula-status', token],
    queryFn: () => consultarStatusMatricula(token),
    enabled: !!token,
    retry: false,
    refetchOnWindowFocus: false,
    staleTime: 0,
    gcTime: 0,
  })

export const useEnviarDocumentos = (token) =>
  useMutation({ mutationFn: (arquivos) => enviarDocumentos(token, arquivos) })
