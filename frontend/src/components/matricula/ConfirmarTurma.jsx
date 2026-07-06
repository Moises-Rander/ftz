import { AlertTriangle, CalendarDays, Clock, Layers, Moon } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { tipoLabel } from '@/lib/format'

const hhmm = (h) => (h ? String(h).slice(0, 5) : '')

export default function ConfirmarTurma({ turma, onContinuar }) {
  const encerrada = turma.status !== 'ABERTA'
  const isGrad = turma.curso_tipo === 'GRADUACAO'
  const ciclo = turma.ciclo_ativo
  const horarios = turma.horarios_formacao || []

  return (
    <Card>
      <CardContent className="space-y-5">
        <div>
          <Badge variant="secondary">{tipoLabel(turma.curso_tipo)}</Badge>
          <h2 className="mt-2 text-2xl font-bold">{turma.curso_nome}</h2>
          <p className="text-muted-foreground">Turma {turma.nome || `#${turma.id}`}</p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="flex items-center gap-2 text-sm">
            <Moon className="h-4 w-4 text-primary" /> Turno: Noturno (presencial)
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Badge variant={turma.vagas_disponiveis > 0 ? 'outline' : 'destructive'}>
              {turma.vagas_disponiveis > 0
                ? `${turma.vagas_disponiveis} vaga(s) disponível(is)`
                : 'Vagas esgotadas'}
            </Badge>
          </div>
        </div>

        {/* Grade / módulo */}
        {isGrad ? (
          ciclo ? (
            <div className="rounded-lg border bg-muted/40 p-4 text-sm">
              <p className="mb-2 font-medium">Ciclo {ciclo.numero} — grade atual</p>
              <ul className="space-y-1 text-muted-foreground">
                {(ciclo.grades || []).map((g) => (
                  <li key={g.id} className="flex items-center gap-2">
                    <CalendarDays className="h-3.5 w-3.5" /> {g.disciplina_nome} — {g.dia_semana_display} {hhmm(g.horario)}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">O calendário do ciclo será divulgado em breve.</p>
          )
        ) : (
          <div className="rounded-lg border bg-muted/40 p-4 text-sm">
            {horarios.length > 0 && (
              <p className="mb-2 flex items-center gap-2 text-muted-foreground">
                <Clock className="h-4 w-4" />
                {horarios
                  .map((h) => `${h.dia_1_display} e ${h.dia_2_display} às ${hhmm(h.horario_inicio)}`)
                  .join(' • ')}
              </p>
            )}
            {turma.modulo_ativo && (
              <p className="flex items-center gap-2">
                <Layers className="h-4 w-4 text-primary" /> Módulo atual:{' '}
                <strong>{turma.modulo_ativo.nome}</strong>
              </p>
            )}
          </div>
        )}

        {encerrada ? (
          <div className="flex items-start gap-3 rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />
            <p>As matrículas para esta turma estão encerradas no momento.</p>
          </div>
        ) : (
          <Button className="w-full sm:w-auto" onClick={onContinuar}>
            Continuar
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
