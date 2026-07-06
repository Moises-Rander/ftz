import { create } from 'zustand'

// Persiste o upload_token da matrícula para sobreviver a reloads (sessionStorage).
const CHAVE = 'ftz_upload_token'

const tokenInicial =
  typeof sessionStorage !== 'undefined' ? sessionStorage.getItem(CHAVE) || '' : ''

export const useMatriculaStore = create((set) => ({
  uploadToken: tokenInicial,

  setUploadToken: (token) => {
    try {
      if (token) sessionStorage.setItem(CHAVE, token)
    } catch {
      /* sessionStorage indisponível — mantém apenas em memória */
    }
    set({ uploadToken: token })
  },

  limparUploadToken: () => {
    try {
      sessionStorage.removeItem(CHAVE)
    } catch {
      /* ignore */
    }
    set({ uploadToken: '' })
  },
}))
