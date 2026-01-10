'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api-client';
import type { FormAnalysisResponse } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react';

// Extended type to match what the component expects
interface AnalysisData extends FormAnalysisResponse {
  workout_id?: number;
  similar_workouts_count?: number;
  analyzed_at?: string;
}

export default function WorkoutAnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const workoutId = params?.id as string;

  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!workoutId) return;

    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);

        // Use the public method instead of accessing private client property
        const response = await apiClient.analyzeWorkoutDeep(parseInt(workoutId));

        // Adapt the response to match AnalysisData interface
        const adaptedResponse: AnalysisData = {
          ...response,
          workout_id: parseInt(workoutId),
          analyzed_at: new Date().toISOString(),
        };

        setAnalysis(adaptedResponse);
      } catch (err: any) {
        console.error('Error fetching analysis:', err);

        if (err.response?.status === 404) {
          setError('Entrenamiento no encontrado');
        } else if (err.response?.status === 401) {
          setError('No autorizado. Por favor inicia sesión.');
        } else if (err.message?.includes('GROQ_API_KEY')) {
          setError('El análisis de IA no está disponible. Configura GROQ_API_KEY.');
        } else {
          setError(err.response?.data?.detail || 'Error al cargar el análisis');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [workoutId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="text-slate-400 hover:text-white mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver
          </Button>
          <h1 className="text-3xl font-bold text-white">Análisis Detallado del Entrenamiento</h1>
          <p className="text-slate-400 mt-2">Análisis completo con recomendaciones personalizadas</p>
        </div>

        {/* Loading State */}
        {loading && (
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardContent className="flex items-center justify-center py-12">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin text-blue-400 mx-auto mb-4" />
                <p className="text-slate-300">Analizando tu entrenamiento...</p>
                <p className="text-sm text-slate-500 mt-2">Esto puede tomar unos segundos</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error State */}
        {error && !loading && (
          <Card className="bg-red-950/50 border-red-800 backdrop-blur">
            <CardContent className="flex items-start gap-4 py-6">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-red-300 font-semibold">Error</h3>
                <p className="text-red-200 text-sm mt-1">{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Analysis Content */}
        {analysis && !loading && (
          <>
            {/* Analysis Card */}
            <Card className="bg-slate-800/50 border-slate-700 backdrop-blur mb-6">
              <CardHeader>
                <CardTitle className="text-white">Análisis AI Coach</CardTitle>
                <CardDescription className="text-slate-400">
                  {analysis.analyzed_at 
                    ? `Análisis realizado el ${new Date(analysis.analyzed_at).toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}`
                    : 'Análisis realizado ahora'
                  }
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="prose prose-invert max-w-none">
                  <div className="text-slate-200 whitespace-pre-wrap leading-relaxed">
                    {analysis.analysis}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Metadata Footer */}
            <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  {analysis.similar_workouts_count !== undefined && (
                    <div>
                      <p className="text-slate-400 text-xs uppercase tracking-wide">Entrenamientos Comparados</p>
                      <p className="text-white text-lg font-semibold mt-1">
                        {analysis.similar_workouts_count}
                      </p>
                    </div>
                  )}
                  <div>
                    <p className="text-slate-400 text-xs uppercase tracking-wide">Tokens Utilizados</p>
                    <p className="text-white text-lg font-semibold mt-1">
                      {analysis.tokens_used || 0}
                    </p>
                  </div>
                  {analysis.workout_id && (
                    <div>
                      <p className="text-slate-400 text-xs uppercase tracking-wide">Workout ID</p>
                      <p className="text-white text-lg font-semibold mt-1">
                        #{analysis.workout_id}
                      </p>
                    </div>
                  )}
                  {analysis.efficiency_rating && (
                    <div>
                      <p className="text-slate-400 text-xs uppercase tracking-wide">Eficiencia</p>
                      <p className="text-white text-lg font-semibold mt-1">
                        {analysis.efficiency_rating}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="flex gap-4 mt-6">
              <Button
                onClick={() => router.push(`/workouts/${workoutId}`)}
                variant="outline"
                className="border-slate-700 hover:bg-slate-800"
              >
                Ver Detalles del Workout
              </Button>
              <Button
                onClick={() => router.push('/dashboard')}
                className="bg-blue-600 hover:bg-blue-700"
              >
                Ir al Dashboard
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
