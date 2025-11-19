'use client';

/**
 * Smart Suggestions Component
 * AI-powered suggestions based on workout data
 */
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Workout } from '@/lib/types';

interface SmartSuggestionsProps {
  workouts: Workout[];
  user: any;
}

export function SmartSuggestions({ workouts, user }: SmartSuggestionsProps) {
  const suggestions: string[] = [];

  if (!workouts || workouts.length === 0) {
    return (
      <Card className="bg-slate-800/50 border-slate-700 animate-fade-in hover:shadow-lg transition-shadow duration-300">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <span>💡</span> Sugerencias Inteligentes
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400 text-center py-6">
            Crea entrenamientos para recibir sugerencias personalizadas
          </p>
        </CardContent>
      </Card>
    );
  }

  // Análisis de últimas 2 semanas
  const twoWeeksAgo = new Date(Date.now() - 14 * 24 * 60 * 60 * 1000);
  const recentWorkouts = workouts.filter(w => new Date(w.start_time) >= twoWeeksAgo);

  if (recentWorkouts.length > 0) {
    // Análisis de intensidad basado en avg_heart_rate (% de max_hr)
    const maxHR = user?.max_heart_rate || 200;
    const avgHRValues = recentWorkouts
      .map(w => w.avg_heart_rate || 0)
      .filter(hr => hr > 0);
    
    if (avgHRValues.length > 0) {
      const avgHRPercent = (avgHRValues.reduce((a, b) => a + b, 0) / avgHRValues.length / maxHR) * 100;
      
      // Z2 estimado: 60-70% max HR
      // Z4/Z5 estimado: 85-95% max HR
      const lowIntensity = recentWorkouts.filter(w => {
        const pct = ((w.avg_heart_rate || 0) / maxHR) * 100;
        return pct >= 60 && pct <= 75;
      }).length;
      
      const highIntensity = recentWorkouts.filter(w => {
        const pct = ((w.avg_heart_rate || 0) / maxHR) * 100;
        return pct >= 85 && pct <= 100;
      }).length;
      
      const totalRecent = recentWorkouts.length;
      
      if (lowIntensity > 0) {
        const z2Percentage = (lowIntensity / totalRecent) * 100;
        if (z2Percentage < 40 && totalRecent >= 3) {
          suggestions.push(`📍 Aumenta entrenamientos moderados - Actual: ${z2Percentage.toFixed(0)}%`);
        } else if (z2Percentage >= 50 && z2Percentage <= 70) {
          suggestions.push(`✅ Excelente balance de entrenamientos moderados - ${z2Percentage.toFixed(0)}%`);
        }
      }
      
      if (highIntensity === 0 && totalRecent >= 4) {
        suggestions.push(`⚡ Agrega entrenamientos de alta intensidad - Mínimo 1-2 por semana`);
      } else if (highIntensity > totalRecent * 0.4) {
        suggestions.push(`⚠️ Posible sobreentrenamiento - Alto % intensidad (${(highIntensity / totalRecent * 100).toFixed(0)}%)`);
      }
    }
  }

  // Defecto si no hay sugerencias específicas
  if (suggestions.length === 0) {
    suggestions.push(`📊 Datos insuficientes - Necesitamos más entrenamientos para análisis`);
    suggestions.push(`✨ Sigue entrenando de forma consistente`);
    suggestions.push(`🎯 Mantén el balance entre Z2 (50-70%) y alta intensidad (10-20%)`);
  }

  // Limita a 3 sugerencias
  const displaySuggestions = suggestions.slice(0, 3);

  return (
    <Card className="bg-slate-800/50 border-slate-700 animate-fade-in hover:shadow-lg transition-shadow duration-300">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <span>💡</span> Sugerencias Inteligentes
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {displaySuggestions.map((sug, idx) => (
            <div
              key={idx}
              className="flex items-start gap-3 p-3 bg-slate-700/30 rounded-lg border border-slate-600 hover:border-slate-500 transition-colors"
            >
              <span className="text-lg flex-shrink-0 mt-0.5">
                {sug.startsWith('✅') && '✅'}
                {sug.startsWith('📍') && '📍'}
                {sug.startsWith('⚡') && '⚡'}
                {sug.startsWith('⚠️') && '⚠️'}
                {sug.startsWith('💤') && '💤'}
                {sug.startsWith('💪') && '💪'}
                {sug.startsWith('📊') && '📊'}
                {sug.startsWith('✨') && '✨'}
                {sug.startsWith('🎯') && '🎯'}
              </span>
              <p className="text-slate-300 text-sm leading-relaxed flex-1">
                {sug.substring(2).trim()}
              </p>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-4 p-3 bg-blue-600/10 rounded-lg border border-blue-500/20">
          <p className="text-blue-300 text-xs">
            💡 <span className="font-semibold">Tip:</span> Las sugerencias se basan en análisis de tus últimos entrenamientos
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
