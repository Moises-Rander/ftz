import { create } from 'zustand'

// Estado global de UI (menu mobile). Simples, mas centraliza no Zustand
// conforme a arquitetura do projeto — pronto para crescer (ex.: auth no V10).
export const useUiStore = create((set) => ({
  mobileMenuAberto: false,
  abrirMobileMenu: () => set({ mobileMenuAberto: true }),
  fecharMobileMenu: () => set({ mobileMenuAberto: false }),
  toggleMobileMenu: () =>
    set((s) => ({ mobileMenuAberto: !s.mobileMenuAberto })),
}))
