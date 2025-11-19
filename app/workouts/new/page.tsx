'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function NewWorkoutPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showOptional, setShowOptional] = useState(false);

  const [formData, setFormData] = useState({
    start_time: new Date().toISOString().slice(0, 16),
    duration_minutes: 45,
    distance_km: 10,
    pace_minutes: 4,
    pace_seconds: 30,
    avg_heart_rate: 150,
    sport_type: 'running',
    max_heart_rate: 170,
    // Opcionales
    elevation_gain: 0,
    avg_cadence: 0,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'start_time' || name === 'sport_type' 
        ? value 
        : parseFloat(value) || 0,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Convertir unidades user-friendly a formato backend
      const paceInSeconds = formData.pace_minutes * 60 + formData.pace_seconds;
      const durationSeconds = formData.duration_minutes * 60;
      const distanceMeters = formData.distance_km * 1000;

      const payload = {
        start_time: new Date(formData.start_time).toISOString(),
        duration_seconds: durationSeconds,
        distance_meters: distanceMeters,
        avg_pace: paceInSeconds,
        sport_type: formData.sport_type,
        ...(formData.avg_heart_rate > 0 && { avg_heart_rate: formData.avg_heart_rate }),
        ...(formData.max_heart_rate > 0 && { max_heart_rate: formData.max_heart_rate }),
        ...(formData.elevation_gain > 0 && { elevation_gain: formData.elevation_gain }),
        ...(formData.avg_cadence > 0 && { avg_cadence: formData.avg_cadence }),
      };

      console.log('Enviando workout:', payload);

      const response = await apiClient.createWorkout(payload);
      console.log('Respuesta:', response);

      router.push('/workouts');
    } catch (err: any) {
      console.error('Error creating workout:', err);
      const detail = err.response?.data?.detail;
      const message = typeof detail === 'string' ? detail : 'Error al crear entrenamiento';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-8">
      <div className="max-w-2xl mx-auto">
        <Card className="border-slate-700 bg-slate-800/50 backdrop-blur">
          <CardHeader>
            <CardTitle className="text-3xl text-white">Nuevo Entrenamiento</CardTitle>
            <CardDescription className="text-slate-400">
              Registra manualmente un entrenamiento
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="p-4 text-red-400 bg-red-950/50 border border-red-800 rounded-lg">
                  {error}
                </div>
              )}

              {/* SECCIÓN 1: BÁSICOS */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white border-b border-slate-700 pb-2">Información Básica</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Tipo de deporte */}
                  <div className="space-y-2">
                    <Label htmlFor="sport_type" className="text-slate-200">Tipo de deporte</Label>
                    <select
                      id="sport_type"
                      name="sport_type"
                      value={formData.sport_type}
                      onChange={handleChange}
                      className="w-full px-3 py-2 bg-slate-900/50 border border-slate-700 text-white rounded-lg focus:outline-none focus:border-blue-500"
                    >
                      <option value="running">🏃 Corrida</option>
                      <option value="cycling">🚴 Ciclismo</option>
                      <option value="swimming">🏊 Natación</option>
                      <option value="walking">🚶 Caminata</option>
                    </select>
                  </div>

                  {/* Fecha y hora */}
                  <div className="space-y-2">
                    <Label htmlFor="start_time" className="text-slate-200">Fecha y hora</Label>
                    <Input
                      id="start_time"
                      name="start_time"
                      type="datetime-local"
                      value={formData.start_time}
                      onChange={handleChange}
                      className="bg-slate-900/50 border-slate-700 text-white"
                    />
                  </div>

                  {/* Duración */}
                  <div className="space-y-2">
                    <Label htmlFor="duration_minutes" className="text-slate-200">Duración</Label>
                    <div className="flex items-center gap-2">
                      <Input
                        id="duration_minutes"
                        name="duration_minutes"
                        type="number"
                        value={formData.duration_minutes}
                        onChange={handleChange}
                        min="1"
                        max="600"
                        className="bg-slate-900/50 border-slate-700 text-white flex-1"
                      />
                      <span className="text-slate-400">min</span>
                    </div>
                  </div>

                  {/* Distancia */}
                  <div className="space-y-2">
                    <Label htmlFor="distance_km" className="text-slate-200">Distancia</Label>
                    <div className="flex items-center gap-2">
                      <Input
                        id="distance_km"
                        name="distance_km"
                        type="number"
                        value={formData.distance_km}
                        onChange={handleChange}
                        min="0"
                        step="0.1"
                        className="bg-slate-900/50 border-slate-700 text-white flex-1"
                      />
                      <span className="text-slate-400">km</span>
                    </div>
                  </div>

                  {/* Pace - Minutos */}
                  <div className="space-y-2">
                    <Label htmlFor="pace_minutes" className="text-slate-200">Ritmo (minutos)</Label>
                    <div className="flex items-center gap-2">
                      <Input
                        id="pace_minutes"
                        name="pace_minutes"
                        type="number"
                        value={formData.pace_minutes}
                        onChange={handleChange}
                        min="0"
                        max="59"
                        className="bg-slate-900/50 border-slate-700 text-white flex-1"
                      />
                      <span className="text-slate-400">:</span>
                      <Input
                        id="pace_seconds"
                        name="pace_seconds"
                        type="number"
                        value={String(formData.pace_seconds).padStart(2, '0')}
                        onChange={(e) => {
                          const val = Math.min(59, parseInt(e.target.value) || 0);
                          handleChange({
                            ...e,
                            target: { ...e.target, name: 'pace_seconds', value: String(val) }
                          });
                        }}
                        min="0"
                        max="59"
                        className="bg-slate-900/50 border-slate-700 text-white w-16"
                      />
                      <span className="text-slate-400">/km</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Ritmo: {formData.pace_minutes}'{String(formData.pace_seconds).padStart(2, '0')}" /km
                    </p>
                  </div>
                </div>
              </div>

              {/* SECCIÓN 2: OPCIONALES */}
              <div className="space-y-4 border-t border-slate-700 pt-4">
                <button
                  type="button"
                  onClick={() => setShowOptional(!showOptional)}
                  className="text-blue-400 hover:text-blue-300 text-sm font-medium"
                >
                  {showOptional ? '▼' : '▶'} Datos opcionales
                </button>

                {showOptional && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    {/* HR promedio */}
                    <div className="space-y-2">
                      <Label htmlFor="avg_heart_rate" className="text-slate-200">Frecuencia cardíaca promedio</Label>
                      <div className="flex items-center gap-2">
                        <Input
                          id="avg_heart_rate"
                          name="avg_heart_rate"
                          type="number"
                          value={formData.avg_heart_rate}
                          onChange={handleChange}
                          min="0"
                          max="300"
                          className="bg-slate-900/50 border-slate-700 text-white flex-1"
                        />
                        <span className="text-slate-400">bpm</span>
                      </div>
                    </div>

                    {/* HR máximo */}
                    <div className="space-y-2">
                      <Label htmlFor="max_heart_rate" className="text-slate-200">Frecuencia cardíaca máxima</Label>
                      <div className="flex items-center gap-2">
                        <Input
                          id="max_heart_rate"
                          name="max_heart_rate"
                          type="number"
                          value={formData.max_heart_rate}
                          onChange={handleChange}
                          min="0"
                          max="300"
                          className="bg-slate-900/50 border-slate-700 text-white flex-1"
                        />
                        <span className="text-slate-400">bpm</span>
                      </div>
                    </div>

                    {/* Desnivel */}
                    <div className="space-y-2">
                      <Label htmlFor="elevation_gain" className="text-slate-200">Desnivel positivo</Label>
                      <div className="flex items-center gap-2">
                        <Input
                          id="elevation_gain"
                          name="elevation_gain"
                          type="number"
                          value={formData.elevation_gain}
                          onChange={handleChange}
                          min="0"
                          step="10"
                          className="bg-slate-900/50 border-slate-700 text-white flex-1"
                        />
                        <span className="text-slate-400">m</span>
                      </div>
                    </div>

                    {/* Cadencia */}
                    <div className="space-y-2">
                      <Label htmlFor="avg_cadence" className="text-slate-200">Cadencia promedio</Label>
                      <div className="flex items-center gap-2">
                        <Input
                          id="avg_cadence"
                          name="avg_cadence"
                          type="number"
                          value={formData.avg_cadence}
                          onChange={handleChange}
                          min="0"
                          step="1"
                          className="bg-slate-900/50 border-slate-700 text-white flex-1"
                        />
                        <span className="text-slate-400">rpm</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* BOTONES */}
              <div className="flex gap-3 pt-4 border-t border-slate-700">
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {isLoading ? 'Guardando...' : 'Guardar Entrenamiento'}
                </Button>
                <Button
                  type="button"
                  onClick={() => router.back()}
                  className="flex-1 bg-slate-700 hover:bg-slate-600 text-white"
                >
                  Cancelar
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
