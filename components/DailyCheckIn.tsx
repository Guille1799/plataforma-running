'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api-client'
import { Smile, Frown, Meh, Battery, HeartPulse, Moon } from 'lucide-react'

const energyLabels = ['😴 Muy bajo', '😑 Bajo', '😐 Normal', '🙂 Bien', '😊 Excelente']
const sorenessLabels = ['✅ Sin molestias', '😌 Ligero', '😐 Moderado', '😬 Dolorido', '😣 Muy dolorido']
const moodLabels = ['😢 Mal', '😕 Bajo', '😐 Normal', '😊 Bien', '😄 Excelente']
const motivationLabels = ['❌ Ninguna', '😑 Poca', '😐 Moderada', '😊 Alta', '🔥 Muy alta']

export function DailyCheckIn() {
  const [energyLevel, setEnergyLevel] = useState(3)
  const [sorenessLevel, setSorenessLevel] = useState(1)
  const [mood, setMood] = useState(3)
  const [motivation, setMotivation] = useState(3)
  const [sleepHours, setSleepHours] = useState('7.5')
  const [restingHR, setRestingHR] = useState('')
  const [notes, setNotes] = useState('')

  const queryClient = useQueryClient()

  const submitMutation = useMutation({
    mutationFn: async () => {
      const data = {
        date: new Date().toISOString().split('T')[0],
        energy_level: energyLevel,
        soreness_level: sorenessLevel,
        mood: mood,
        motivation: motivation,
        sleep_duration_minutes: sleepHours ? Math.round(parseFloat(sleepHours) * 60) : undefined,
        resting_hr_bpm: restingHR ? parseInt(restingHR) : undefined,
        notes: notes || undefined,
      }
      return apiClient.createManualHealthMetric(data)
    },
    onSuccess: () => {
      toast.success('✅ Check-in guardado exitosamente')
      queryClient.invalidateQueries({ queryKey: ['health'] })
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.response?.data?.detail || error.message}`)
    },
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <HeartPulse className="h-5 w-5" />
          Check-In Diario
        </CardTitle>
        <CardDescription>
          ¿Cómo te sientes hoy? Esto ayuda al Coach IA a personalizar tus entrenamientos
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Energy Level */}
        <div className="space-y-2">
          <Label className="flex items-center gap-2">
            <Battery className="h-4 w-4" />
            Nivel de energía
          </Label>
          <Slider
            value={[energyLevel]}
            onValueChange={([v]) => setEnergyLevel(v)}
            min={1}
            max={5}
            step={1}
            className="py-4"
          />
          <div className="flex justify-between text-sm">
            {energyLabels.map((label, idx) => (
              <span
                key={idx}
                className={`text-xs ${energyLevel === idx + 1 ? 'font-bold text-primary' : 'text-muted-foreground'}`}
              >
                {label.split(' ')[0]}
              </span>
            ))}
          </div>
          <p className="text-sm font-medium text-center">{energyLabels[energyLevel - 1]}</p>
        </div>

        {/* Soreness Level */}
        <div className="space-y-2">
          <Label>Nivel de molestias musculares</Label>
          <Slider
            value={[sorenessLevel]}
            onValueChange={([v]) => setSorenessLevel(v)}
            min={1}
            max={5}
            step={1}
            className="py-4"
          />
          <div className="flex justify-between text-sm">
            {sorenessLabels.map((label, idx) => (
              <span
                key={idx}
                className={`text-xs ${sorenessLevel === idx + 1 ? 'font-bold text-primary' : 'text-muted-foreground'}`}
              >
                {label.split(' ')[0]}
              </span>
            ))}
          </div>
          <p className="text-sm font-medium text-center">{sorenessLabels[sorenessLevel - 1]}</p>
        </div>

        {/* Mood */}
        <div className="space-y-2">
          <Label className="flex items-center gap-2">
            <Smile className="h-4 w-4" />
            Estado de ánimo
          </Label>
          <Slider
            value={[mood]}
            onValueChange={([v]) => setMood(v)}
            min={1}
            max={5}
            step={1}
            className="py-4"
          />
          <p className="text-sm font-medium text-center">{moodLabels[mood - 1]}</p>
        </div>

        {/* Motivation */}
        <div className="space-y-2">
          <Label>Motivación para entrenar</Label>
          <Slider
            value={[motivation]}
            onValueChange={([v]) => setMotivation(v)}
            min={1}
            max={5}
            step={1}
            className="py-4"
          />
          <p className="text-sm font-medium text-center">{motivationLabels[motivation - 1]}</p>
        </div>

        {/* Sleep Duration */}
        <div className="space-y-2">
          <Label htmlFor="sleep" className="flex items-center gap-2">
            <Moon className="h-4 w-4" />
            Horas de sueño
          </Label>
          <Input
            id="sleep"
            type="number"
            step="0.5"
            min="0"
            max="12"
            value={sleepHours}
            onChange={(e) => setSleepHours(e.target.value)}
            placeholder="7.5"
          />
        </div>

        {/* Resting HR (optional) */}
        <div className="space-y-2">
          <Label htmlFor="hr">FC en reposo (opcional)</Label>
          <Input
            id="hr"
            type="number"
            min="30"
            max="200"
            value={restingHR}
            onChange={(e) => setRestingHR(e.target.value)}
            placeholder="ej: 52"
          />
          <p className="text-xs text-muted-foreground">
            Mídelo al despertar antes de levantarte de la cama
          </p>
        </div>

        {/* Notes */}
        <div className="space-y-2">
          <Label htmlFor="notes">Notas (opcional)</Label>
          <Textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="¿Cómo te sientes? ¿Algo que quieras comentar sobre tu estado?"
            rows={3}
          />
        </div>

        {/* Submit Button */}
        <Button
          onClick={() => submitMutation.mutate()}
          disabled={submitMutation.isPending}
          className="w-full"
          size="lg"
        >
          {submitMutation.isPending ? 'Guardando...' : 'Guardar Check-In'}
        </Button>
      </CardContent>
    </Card>
  )
}
