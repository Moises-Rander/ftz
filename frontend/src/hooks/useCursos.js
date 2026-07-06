import { useQuery } from '@tanstack/react-query'
import {
  listarCursos,
  obterCurso,
  listarTurmasDoCurso,
  obterTurma,
  listarProfessoresDaTurma,
} from '@/services/cursos'

export const useCursos = (filtros = {}) =>
  useQuery({
    queryKey: ['cursos', filtros],
    queryFn: () => listarCursos(filtros),
  })

export const useCurso = (id) =>
  useQuery({
    queryKey: ['curso', id],
    queryFn: () => obterCurso(id),
    enabled: !!id,
  })

export const useTurmasDoCurso = (id) =>
  useQuery({
    queryKey: ['curso', id, 'turmas'],
    queryFn: () => listarTurmasDoCurso(id),
    enabled: !!id,
  })

export const useTurma = (id) =>
  useQuery({
    queryKey: ['turma', id],
    queryFn: () => obterTurma(id),
    enabled: !!id,
  })

export const useProfessoresDaTurma = (id) =>
  useQuery({
    queryKey: ['turma', id, 'professores'],
    queryFn: () => listarProfessoresDaTurma(id),
    enabled: !!id,
  })
