import { useMutation, useQuery } from '@tanstack/react-query'
import {
  listarMinhasMatriculas,
  gradeCompleta,
  boletim,
  frequencia,
  avaliacoes,
  trabalhos,
  entregarTrabalho,
} from '@/services/aluno'

export const useMinhasMatriculas = () =>
  useQuery({ queryKey: ['minhas-matriculas'], queryFn: listarMinhasMatriculas })

export const useGradeCompleta = (turmaId) =>
  useQuery({
    queryKey: ['grade-completa', turmaId],
    queryFn: () => gradeCompleta(turmaId),
    enabled: !!turmaId,
  })

export const useBoletim = (turmaId) =>
  useQuery({ queryKey: ['boletim', turmaId], queryFn: () => boletim(turmaId), enabled: !!turmaId })

export const useFrequencia = (turmaId) =>
  useQuery({ queryKey: ['frequencia', turmaId], queryFn: () => frequencia(turmaId), enabled: !!turmaId })

export const useAvaliacoes = (turmaId) =>
  useQuery({ queryKey: ['avaliacoes-aluno', turmaId], queryFn: () => avaliacoes(turmaId), enabled: !!turmaId })

export const useTrabalhos = (turmaId) =>
  useQuery({ queryKey: ['trabalhos-aluno', turmaId], queryFn: () => trabalhos(turmaId), enabled: !!turmaId })

export const useEntregarTrabalho = () =>
  useMutation({ mutationFn: ({ trabalhoId, arquivo }) => entregarTrabalho(trabalhoId, arquivo) })
