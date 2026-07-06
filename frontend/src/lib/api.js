import axios from 'axios'
import { API_URL } from '@/lib/config'
import { useAuthStore } from '@/stores/useAuthStore'

// Instância central do Axios. A URL base vem de VITE_API_URL.
export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// --- Request: injeta o Bearer token quando autenticado ---
api.interceptors.request.use((config) => {
  const { access } = useAuthStore.getState()
  if (access) config.headers.Authorization = `Bearer ${access}`
  return config
})

// --- Response: refresh automático (uma vez) em 401 ---
let refreshPromise = null

function renovarAccess() {
  if (!refreshPromise) {
    const { refresh } = useAuthStore.getState()
    if (!refresh) return Promise.reject(new Error('sem refresh token'))
    // axios "cru" para não passar pelos interceptors (evita recursão).
    refreshPromise = axios
      .post(`${API_URL.replace(/\/$/, '')}/auth/refresh/`, { refresh })
      .then((res) => {
        const { access, refresh: novoRefresh } = res.data
        useAuthStore.getState().setAccess(access, novoRefresh)
        return access
      })
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}

const semRefresh = (url = '') =>
  url.includes('/auth/refresh') || url.includes('/auth/login')

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const status = error.response?.status

    if (status === 401 && original && !original._retry && !semRefresh(original.url)) {
      original._retry = true
      try {
        const novoAccess = await renovarAccess()
        original.headers = original.headers || {}
        original.headers.Authorization = `Bearer ${novoAccess}`
        return api(original)
      } catch {
        // Refresh falhou → desloga e manda para o login.
        useAuthStore.getState().logout()
        if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
          window.location.assign('/login')
        }
        return Promise.reject(error)
      }
    }
    return Promise.reject(error)
  }
)

// Mensagem de erro amigável (sem expor detalhes técnicos ao usuário).
export function mensagemErro(error, fallback = 'Não foi possível carregar as informações. Tente novamente em instantes.') {
  const status = error?.response?.status
  if (status === 404) return 'Conteúdo não encontrado.'
  if (status >= 500) return 'Nossos servidores estão indisponíveis no momento. Tente novamente mais tarde.'
  return fallback
}

export default api
