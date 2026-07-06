import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { UserRound } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Spinner, ErrorState } from '@/components/common/StateComponents'
import AlterarSenha from '@/components/portal/AlterarSenha'
import { useMe, useUpdateMe } from '@/hooks/useAuth'
import { useAuthStore } from '@/stores/useAuthStore'

function DadosProfessor({ me }) {
  const queryClient = useQueryClient()
  const setUser = useAuthStore((s) => s.setUser)
  const atualizar = useUpdateMe()

  const [form, setForm] = useState({
    first_name: me.first_name || '',
    last_name: me.last_name || '',
    titulacao: me.titulacao || '',
    bio: me.bio || '',
  })
  const [foto, setFoto] = useState(null)
  const [preview, setPreview] = useState(me.foto || '')

  const onFoto = (file) => {
    setFoto(file)
    if (file) setPreview(URL.createObjectURL(file))
  }

  const salvar = (e) => {
    e.preventDefault()
    const payload = { ...form }
    if (foto) payload.foto = foto
    atualizar.mutate(payload, {
      onSuccess: (data) => {
        toast.success('Perfil atualizado.')
        setUser({ nome: `${data.first_name} ${data.last_name}`.trim() })
        queryClient.invalidateQueries({ queryKey: ['me'] })
      },
      onError: () => toast.error('Não foi possível salvar o perfil.'),
    })
  }

  return (
    <Card>
      <CardContent>
        <h2 className="text-lg font-semibold">Dados do professor</h2>
        <form onSubmit={salvar} className="mt-5 space-y-4">
          <div className="flex items-center gap-4">
            <Avatar className="h-20 w-20">
              <AvatarImage src={preview} alt="Foto de perfil" />
              <AvatarFallback>
                <UserRound className="h-8 w-8" />
              </AvatarFallback>
            </Avatar>
            <div>
              <Label htmlFor="foto">Foto de perfil</Label>
              <Input id="foto" type="file" accept="image/*" className="mt-1" onChange={(e) => onFoto(e.target.files?.[0] || null)} />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="first_name">Nome</Label>
              <Input id="first_name" value={form.first_name} onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="last_name">Sobrenome</Label>
              <Input id="last_name" value={form.last_name} onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))} />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="email">Email (somente leitura)</Label>
            <Input id="email" value={me.email} readOnly disabled />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="titulacao">Titulação</Label>
            <Input id="titulacao" value={form.titulacao} onChange={(e) => setForm((f) => ({ ...f, titulacao: e.target.value }))} placeholder="Ex.: Doutor em Teologia" />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="bio">Bio</Label>
            <Textarea id="bio" rows={4} value={form.bio} onChange={(e) => setForm((f) => ({ ...f, bio: e.target.value }))} />
          </div>

          <Button type="submit" disabled={atualizar.isPending}>
            {atualizar.isPending ? 'Salvando...' : 'Salvar alterações'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

export default function PerfilProfessor() {
  const { data: me, isLoading, isError, refetch } = useMe()

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold tracking-tight">Meu perfil</h1>
      {isLoading && <Spinner />}
      {isError && <ErrorState onRetry={refetch} />}
      {me && (
        <>
          <DadosProfessor me={me} />
          <AlterarSenha />
        </>
      )}
    </div>
  )
}
