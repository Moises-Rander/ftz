import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Store de autenticação — persistido no localStorage.
export const useAuthStore = create(
  persist(
    (set, get) => ({
      access: null,
      refresh: null,
      user: null,

      isAutenticado: () => Boolean(get().access),

      // Login: salva tokens + dados do usuário.
      login: ({ access, refresh, user }) => set({ access, refresh, user }),

      // Atualiza campos do usuário (ex.: nome após editar o perfil).
      setUser: (parcial) => set((s) => ({ user: { ...s.user, ...parcial } })),

      // Refresh: atualiza o access (e o refresh, se rotacionado).
      setAccess: (access, refresh) =>
        set((s) => ({ access, refresh: refresh ?? s.refresh })),

      // Logout: limpa tudo.
      logout: () => set({ access: null, refresh: null, user: null }),
    }),
    { name: 'ftz-auth' }
  )
)
