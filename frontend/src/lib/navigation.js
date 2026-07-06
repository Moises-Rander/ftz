// Navegação compartilhada por Navbar e Footer.
export const NAV_LINKS = [
  { label: 'Início', to: '/' },
  {
    label: 'Cursos',
    to: '/cursos',
    children: [
      { label: 'Graduação', to: '/cursos?tipo=GRADUACAO' },
      { label: 'Formação', to: '/cursos?tipo=FORMACAO' },
    ],
  },
  { label: 'Vestibular', to: '/vestibular' },
  { label: 'Sobre', to: '/sobre' },
  { label: 'Blog', to: '/blog' },
  { label: 'Contato', to: '/contato' },
]
