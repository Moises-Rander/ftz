import api from '@/lib/api'

export const login = async (email, password) => {
  const { data } = await api.post('/auth/login/', { email, password })
  return data // { access, refresh, user }
}

export const logout = async (refresh) => {
  // Best-effort: invalida o refresh (blacklist). Ignora falha de rede.
  try {
    await api.post('/auth/logout/', { refresh })
  } catch {
    /* ignore */
  }
}

export const solicitarReset = async (email) => {
  const { data } = await api.post('/auth/password-reset/', { email })
  return data
}

export const confirmarReset = async ({ uid, token, new_password, new_password_confirm }) => {
  const { data } = await api.post('/auth/password-reset/confirm/', {
    uid,
    token,
    new_password,
    new_password_confirm,
  })
  return data
}

export const getMe = async () => {
  const { data } = await api.get('/auth/me/')
  return data
}

export const updateMe = async (payload) => {
  // Se houver arquivo (foto), envia multipart; senão, JSON.
  const temArquivo = payload.foto instanceof File
  if (temArquivo) {
    const fd = new FormData()
    Object.entries(payload).forEach(([k, v]) => {
      if (v !== undefined && v !== null) fd.append(k, v)
    })
    const { data } = await api.patch('/auth/me/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  }
  const { foto: _foto, ...resto } = payload
  const { data } = await api.patch('/auth/me/', resto)
  return data
}

export const alterarSenha = async ({ old_password, new_password, new_password_confirm }) => {
  const { data } = await api.post('/auth/change-password/', {
    old_password,
    new_password,
    new_password_confirm,
  })
  return data
}
