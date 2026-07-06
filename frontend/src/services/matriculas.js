import api from '@/lib/api'

export const iniciarMatricula = async (payload) => {
  const { data } = await api.post('/matriculas/', payload)
  return data
}

export const consultarStatusMatricula = async (token) => {
  const { data } = await api.get('/matriculas/status/', { params: { token } })
  return data
}

// arquivos: objeto { TIPO: File } (ex.: { RG: file, CPF: file })
export const enviarDocumentos = async (token, arquivos) => {
  const fd = new FormData()
  fd.append('token', token)
  Object.entries(arquivos).forEach(([tipo, file]) => fd.append(tipo, file))
  const { data } = await api.post('/matriculas/documentos/', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
