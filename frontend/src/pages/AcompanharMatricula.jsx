import { useState } from 'react'
import { Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import PageHeader from '@/components/common/PageHeader'
import StatusDocumentos from '@/components/matricula/StatusDocumentos'
import { useMatriculaStore } from '@/stores/useMatriculaStore'

export default function AcompanharMatricula() {
  const { uploadToken, setUploadToken } = useMatriculaStore()
  const [input, setInput] = useState(uploadToken || '')
  const [tokenAtivo, setTokenAtivo] = useState(uploadToken || '')

  const consultar = (e) => {
    e.preventDefault()
    const t = input.trim()
    if (!t) return
    setUploadToken(t)
    setTokenAtivo(t)
  }

  return (
    <>
      <PageHeader
        title="Acompanhar matrícula"
        subtitle="Consulte o andamento da sua matrícula usando o código (token) recebido por email."
      />
      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6 lg:px-8">
        <Card>
          <CardContent>
            <form onSubmit={consultar} className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <div className="flex-1 space-y-1.5">
                <Label htmlFor="token">Código de acompanhamento</Label>
                <Input
                  id="token"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Cole aqui o token recebido por email"
                />
              </div>
              <Button type="submit" disabled={!input.trim()}>
                <Search className="mr-2 h-4 w-4" /> Acompanhar
              </Button>
            </form>
          </CardContent>
        </Card>

        {tokenAtivo && (
          <div className="mt-6">
            <StatusDocumentos token={tokenAtivo} />
          </div>
        )}
      </div>
    </>
  )
}
