'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PlanCalendar } from '@/components/training-plan/plan-calendar';
import { WorkoutCard } from '@/components/training-plan/workout-card';
import { ArrowLeft, Calendar, List, TrendingUp, BarChart3, Edit, Download, Archive } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default function TrainingPlanDetailPage() {
  const params = useParams();
  const router = useRouter();
  const planId = params.plan_id as string;

  // Fetch plan details
  const { data: planData, isLoading, error } = useQuery({
    queryKey: ['training-plan', planId],
    queryFn: async () => {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/v1/training-plans/${planId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );
      if (!response.ok) throw new Error('Failed to fetch plan');
      const data = await response.json();
      return data.plan;
    },
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-12">
            <Spinner className="h-8 w-8" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !planData) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <Button
            onClick={() => router.back()}
            variant="outline"
            className="mb-6 border-slate-700"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="pt-6">
              <div className="text-red-400">
                {error ? `Error: ${String(error)}` : 'Plan no encontrado'}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Calculate progress
  const currentWeek = planData.current_week || 1;
  const totalWeeks = planData.total_weeks || planData.weeks?.length || 1;
  const progress = (currentWeek / totalWeeks) * 100;
  const weeksCompleted = currentWeek - 1;
  const weeksRemaining = totalWeeks - currentWeek;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/20 text-green-400 border-green-500/50';
      case 'completed':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
      case 'paused':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
      case 'archived':
        return 'bg-gray-500/20 text-gray-400 border-gray-500/50';
      default:
        return 'bg-slate-700 text-slate-300 border-slate-600';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active':
        return 'Activo';
      case 'completed':
        return 'Completado';
      case 'paused':
        return 'Pausado';
      case 'archived':
        return 'Archivado';
      default:
        return status;
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Button
            onClick={() => router.push('/training-plans')}
            variant="outline"
            className="mb-4 border-slate-700"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver a Lista
          </Button>
          
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-4xl font-bold text-white">
                  {planData.plan_name || 'Plan de Entrenamiento'}
                </h1>
                <Badge className={getStatusColor(planData.status || 'active')}>
                  {getStatusLabel(planData.status || 'active')}
                </Badge>
              </div>
              
              {/* Summary Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardContent className="pt-4">
                    <div className="text-2xl font-bold text-white">{Math.round(progress)}%</div>
                    <div className="text-sm text-slate-400">Progreso</div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardContent className="pt-4">
                    <div className="text-2xl font-bold text-white">{weeksCompleted}</div>
                    <div className="text-sm text-slate-400">Semanas Completadas</div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardContent className="pt-4">
                    <div className="text-2xl font-bold text-white">{weeksRemaining}</div>
                    <div className="text-sm text-slate-400">Semanas Restantes</div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardContent className="pt-4">
                    <div className="text-2xl font-bold text-white">{totalWeeks}</div>
                    <div className="text-sm text-slate-400">Total de Semanas</div>
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col gap-2 ml-4">
              <Button variant="outline" size="sm" className="border-slate-700">
                <Edit className="h-4 w-4 mr-2" />
                Editar
              </Button>
              <Button variant="outline" size="sm" className="border-slate-700">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
              <Button variant="outline" size="sm" className="border-slate-700">
                <Archive className="h-4 w-4 mr-2" />
                Archivar
              </Button>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <Card className="bg-slate-800/50 border-slate-700 mb-6">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">Progreso General</span>
              <span className="text-sm font-semibold text-white">
                Semana {currentWeek} de {totalWeeks}
              </span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all"
                style={{ width: `${Math.min(progress, 100)}%` }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs defaultValue="calendar" className="space-y-4">
          <TabsList className="bg-slate-800/50 border border-slate-700">
            <TabsTrigger value="calendar" className="data-[state=active]:bg-slate-700">
              <Calendar className="h-4 w-4 mr-2" />
              Calendario
            </TabsTrigger>
            <TabsTrigger value="weeks" className="data-[state=active]:bg-slate-700">
              <List className="h-4 w-4 mr-2" />
              Semanas
            </TabsTrigger>
            <TabsTrigger value="progress" className="data-[state=active]:bg-slate-700">
              <TrendingUp className="h-4 w-4 mr-2" />
              Progreso
            </TabsTrigger>
            <TabsTrigger value="metrics" className="data-[state=active]:bg-slate-700">
              <BarChart3 className="h-4 w-4 mr-2" />
              Métricas
            </TabsTrigger>
          </TabsList>

          <TabsContent value="calendar" className="space-y-4">
            <PlanCalendar plan={planData} />
          </TabsContent>

          <TabsContent value="weeks" className="space-y-4">
            <WeeksView plan={planData} />
          </TabsContent>

          <TabsContent value="progress" className="space-y-4">
            <ProgressView plan={planData} />
          </TabsContent>

          <TabsContent value="metrics" className="space-y-4">
            <MetricsView plan={planData} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// Weeks View Component
function WeeksView({ plan }: { plan: any }) {
  const [expandedWeeks, setExpandedWeeks] = useState<Set<number>>(new Set([plan.current_week || 1]));

  const toggleWeek = (weekNum: number) => {
    setExpandedWeeks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(weekNum)) {
        newSet.delete(weekNum);
      } else {
        newSet.add(weekNum);
      }
      return newSet;
    });
  };

  return (
    <div className="space-y-4">
      {plan.weeks?.map((week: any, idx: number) => {
        const weekNum = week.week || idx + 1;
        const isExpanded = expandedWeeks.has(weekNum);
        const isCurrentWeek = weekNum === (plan.current_week || 1);

        return (
          <Card
            key={idx}
            className={`bg-slate-800/50 border-slate-700 ${isCurrentWeek ? 'ring-2 ring-blue-500' : ''}`}
          >
            <CardHeader>
              <div
                className="flex items-center justify-between cursor-pointer"
                onClick={() => toggleWeek(weekNum)}
              >
                <div>
                  <CardTitle className="text-white flex items-center gap-2">
                    Semana {weekNum}
                    {isCurrentWeek && (
                      <Badge className="bg-blue-600 text-white">Actual</Badge>
                    )}
                  </CardTitle>
                  <p className="text-slate-400 text-sm mt-1">
                    {week.focus || 'Entrenamiento'}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold text-white">
                    {week.total_km?.toFixed(1) || 0} km
                  </div>
                  <div className="text-xs text-slate-400">
                    {week.workouts?.length || 0} entrenamientos
                  </div>
                </div>
              </div>
            </CardHeader>
            {isExpanded && (
              <CardContent>
                <div className="space-y-3">
                  {week.workouts?.map((workout: any, workoutIdx: number) => (
                    <WorkoutCard 
                      key={workoutIdx} 
                      workout={workout} 
                      weekNum={weekNum}
                      onComplete={(workout) => {
                        // TODO: Implement workout completion
                        console.log('Complete workout:', workout);
                      }}
                    />
                  ))}
                </div>
              </CardContent>
            )}
          </Card>
        );
      })}
    </div>
  );
}


// Progress View Component (placeholder - will be improved in phase3-tracking)
function ProgressView({ plan }: { plan: any }) {
  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">Progreso y Adherencia</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center text-slate-400 py-12">
          <p className="mb-2">Vista de progreso en desarrollo</p>
          <p className="text-sm">Próximamente: gráficos de cumplimiento, volumen semanal y adherencia</p>
        </div>
      </CardContent>
    </Card>
  );
}

// Metrics View Component (placeholder - will be improved in phase3-tracking)
function MetricsView({ plan }: { plan: any }) {
  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">Métricas: Planificado vs Realizado</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center text-slate-400 py-12">
          <p className="mb-2">Vista de métricas en desarrollo</p>
          <p className="text-sm">Próximamente: comparativa de distancia, ritmo y frecuencia cardíaca</p>
        </div>
      </CardContent>
    </Card>
  );
}
