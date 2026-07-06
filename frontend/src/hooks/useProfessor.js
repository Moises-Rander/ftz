import { useMutation, useQuery } from '@tanstack/react-query'
import {
  minhasTurmas,
  turmaAlunos,
  turmaAulas,
  getFrequencia,
  salvarFrequencia,
  turmaAvaliacoes,
  getResultados,
  salvarResultados,
  turmaTrabalhos,
  trabalhoEntregas,
  corrigirEntrega,
} from '@/services/professor'

export const useMinhasTurmasProfessor = () =>
  useQuery({ queryKey: ['prof-turmas'], queryFn: minhasTurmas })

export const useTurmaAlunos = (turmaId) =>
  useQuery({ queryKey: ['prof-alunos', turmaId], queryFn: () => turmaAlunos(turmaId), enabled: !!turmaId })

export const useTurmaAulas = (turmaId) =>
  useQuery({ queryKey: ['prof-aulas', turmaId], queryFn: () => turmaAulas(turmaId), enabled: !!turmaId })

export const useFrequenciaAula = (aulaId, enabled) =>
  useQuery({ queryKey: ['prof-frequencia', aulaId], queryFn: () => getFrequencia(aulaId), enabled: !!aulaId && enabled })

export const useSalvarFrequencia = (aulaId) =>
  useMutation({ mutationFn: (itens) => salvarFrequencia(aulaId, itens) })

export const useTurmaAvaliacoes = (turmaId) =>
  useQuery({ queryKey: ['prof-avaliacoes', turmaId], queryFn: () => turmaAvaliacoes(turmaId), enabled: !!turmaId })

export const useResultadosAvaliacao = (avaliacaoId, enabled) =>
  useQuery({ queryKey: ['prof-resultados', avaliacaoId], queryFn: () => getResultados(avaliacaoId), enabled: !!avaliacaoId && enabled })

export const useSalvarResultados = (avaliacaoId) =>
  useMutation({ mutationFn: (itens) => salvarResultados(avaliacaoId, itens) })

export const useTurmaTrabalhos = (turmaId) =>
  useQuery({ queryKey: ['prof-trabalhos', turmaId], queryFn: () => turmaTrabalhos(turmaId), enabled: !!turmaId })

export const useTrabalhoEntregas = (trabalhoId, enabled) =>
  useQuery({ queryKey: ['prof-entregas', trabalhoId], queryFn: () => trabalhoEntregas(trabalhoId), enabled: !!trabalhoId && enabled })

export const useCorrigirEntrega = (entregaId) =>
  useMutation({ mutationFn: (payload) => corrigirEntrega(entregaId, payload) })
