'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "@/components/ui/dialog";
import { apiClient } from '@/lib/api-client';
import { TrainingPlanFormV2 } from '../dashboard/training-plan-form-v2';
import { TrainingPlanDetail } from '../dashboard/training-plan-detail';
import { 
  Plus, 
  Search, 
  Filter, 
  Calendar, 
  Target, 
  TrendingUp, 
  Eye,
  Archive,
  MoreVertical,
  Play,
  Pause,
  CheckCircle2,
  X
} from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface PlanSummary {
  plan_id: string;
  plan_name: string;
  goal_type: string;
  goal_date: string;
  total_weeks: number;
  current_week: number;
  created_at: string;
  status: string;
}

type StatusFilter = 'all' | 'active' | 'completed' | 'paused' | 'archived';

export default function TrainingPlansPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { userProfile } = useAuth();
  const [createdPlan, setCreatedPlan] = useState<any>(null);
  const [showForm, setShowForm] = useState(false);
  const [showSyncModal, setShowSyncModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');

  // Fetch training plans
  const { data: plans = [], isLoading, error } = useQuery<PlanSummary[]>({
    queryKey: ['training-plans'],
    queryFn: () => apiClient.getTrainingPlans(),
  });

  // Check if user has Garmin and workouts synced
  const { data: workoutsData, isLoading: isLoadingWorkouts } = useQuery({
    queryKey: ['workouts', 'count'],
    queryFn: () => apiClient.getWorkouts(0, 1),
    retry: 1,
  });

  const workouts = workoutsData?.workouts || (Array.isArray(workoutsData) ? workoutsData : []);
  const hasGarmin = userProfile?.primary_device === 'garmin';
  // Check if user has Garmin-synced workouts specifically (not manual workouts)
  const hasGarminWorkouts = Array.isArray(workouts) && workouts.some((w: any) => 
    w.source_type === 'garmin_fit' || 
    w.source_type === 'garmin_oauth' ||
    w.source === 'garmin_fit' ||
    w.source === 'garmin_oauth'
  );
  const hasWorkouts = Array.isArray(workouts) && workouts.length > 0;

  // Debug: Log values when they change
  useEffect(() => {
    console.log('[TrainingPlans] State update:', {
      hasGarmin,
      hasGarminWorkouts,
      hasWorkouts,
      isLoadingWorkouts,
      workoutsCount: Array.isArray(workouts) ? workouts.length : 'not array',
      userProfile: userProfile ? 'loaded' : 'null',
      primary_device: userProfile?.primary_device,
      workoutsData: workoutsData ? 'loaded' : 'null',
      workoutSources: Array.isArray(workouts) ? workouts.map((w: any) => w.source_type || w.source || 'unknown') : []
    });
  }, [hasGarmin, hasGarminWorkouts, hasWorkouts, isLoadingWorkouts, workouts, userProfile, workoutsData]);

  // Handle "Nuevo Plan" button click
  const handleNewPlanClick = () => {
    // Wait for userProfile to load if not ready
    if (!userProfile) {
      console.log('[TrainingPlans] userProfile not loaded yet, waiting...');
      // Show form anyway, modal logic will be handled by form if needed
      setShowForm(true);
      return;
    }

    console.log('[TrainingPlans] handleNewPlanClick:', {
      hasGarmin,
      hasGarminWorkouts,
      hasWorkouts,
      isLoadingWorkouts,
      workoutsCount: Array.isArray(workouts) ? workouts.length : 'not array',
      userProfile: userProfile ? 'loaded' : 'null',
      primary_device: userProfile?.primary_device,
      workoutSources: Array.isArray(workouts) ? workouts.map((w: any) => w.source_type || w.source || 'unknown') : []
    });
    
    // Show modal if: Garmin user, no Garmin-synced workouts, and not loading
    if (hasGarmin && !hasGarminWorkouts && !isLoadingWorkouts) {
      console.log('[TrainingPlans] Showing sync modal');
      setShowSyncModal(true);
    } else {
      console.log('[TrainingPlans] Showing form directly');
      setShowForm(true);
    }
  };

  // Filter and search plans
  const filteredPlans = useMemo(() => {
    return plans.filter(plan => {
      // Status filter
      if (statusFilter !== 'all' && plan.status !== statusFilter) {
        return false;
      }
      // Search filter
      if (searchQuery && !plan.plan_name.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      return true;
    });
  }, [plans, statusFilter, searchQuery]);

  // Statistics
  const stats = useMemo(() => {
    const active = plans.filter(p => p.status === 'active').length;
    const completed = plans.filter(p => p.status === 'completed').length;
    const paused = plans.filter(p => p.status === 'paused').length;
    const total = plans.length;
    return { active, completed, paused, total };
  }, [plans]);

  // Status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async ({ planId, status }: { planId: string; status: string }) => {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/v1/training-plans/${planId}/status?status=${status}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
        }
      );
      if (!response.ok) throw new Error('Failed to update status');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['training-plans'] });
    },
  });

  if (createdPlan) {
    return (
      <div className="p-8">
        <div className="max-w-6xl mx-auto">
          <button
            onClick={() => setCreatedPlan(null)}
            className="mb-6 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm"
          >
            ← Volver a lista
          </button>
          <TrainingPlanDetail plan={createdPlan} />
        </div>
      </div>
    );
  }

  if (showForm) {
    return (
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => setShowForm(false)}
            className="mb-6 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm"
          >
            ← Volver a lista
          </button>
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white text-2xl">Nuevo Plan de Entrenamiento</CardTitle>
            </CardHeader>
            <CardContent>
              <TrainingPlanFormV2
                onPlanCreated={(plan) => {
                  queryClient.invalidateQueries({ queryKey: ['training-plans'] });
                  setCreatedPlan(plan);
                  setShowForm(false);
                }}
              />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

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

  const getGoalTypeLabel = (goalType: string) => {
    const labels: Record<string, string> = {
      '5k': '5K',
      '10k': '10K',
      'half_marathon': 'Media Maratón',
      'marathon': 'Maratón',
      'improve_fitness': 'Mejorar Fitness',
      'build_endurance': 'Construir Resistencia',
    };
    return labels[goalType] || goalType;
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">
              Planes de Entrenamiento 📋
            </h1>
            <p className="text-slate-400">
              Gestiona tus planes de entrenamiento personalizados
            </p>
          </div>
          <Button
            onClick={handleNewPlanClick}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            Nuevo Plan
          </Button>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-white">{stats.total}</div>
              <div className="text-sm text-slate-400">Total de Planes</div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-green-400">{stats.active}</div>
              <div className="text-sm text-slate-400">Activos</div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-blue-400">{stats.completed}</div>
              <div className="text-sm text-slate-400">Completados</div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-yellow-400">{stats.paused}</div>
              <div className="text-sm text-slate-400">Pausados</div>
            </CardContent>
          </Card>
        </div>

        {/* Filters and Search */}
        <Card className="bg-slate-800/50 border-slate-700 mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  type="text"
                  placeholder="Buscar por nombre..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-slate-900/50 border-slate-700 text-white"
                />
              </div>
              
              {/* Status Filter */}
              <div className="flex gap-2 flex-wrap">
                <Button
                  variant={statusFilter === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter('all')}
                  className={statusFilter === 'all' ? 'bg-blue-600' : ''}
                >
                  Todos
                </Button>
                <Button
                  variant={statusFilter === 'active' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter('active')}
                  className={statusFilter === 'active' ? 'bg-green-600' : ''}
                >
                  Activos
                </Button>
                <Button
                  variant={statusFilter === 'completed' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter('completed')}
                  className={statusFilter === 'completed' ? 'bg-blue-600' : ''}
                >
                  Completados
                </Button>
                <Button
                  variant={statusFilter === 'paused' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter('paused')}
                  className={statusFilter === 'paused' ? 'bg-yellow-600' : ''}
                >
                  Pausados
                </Button>
                <Button
                  variant={statusFilter === 'archived' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter('archived')}
                  className={statusFilter === 'archived' ? 'bg-gray-600' : ''}
                >
                  Archivados
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Plans List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Spinner className="h-8 w-8" />
          </div>
        ) : error ? (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="pt-6">
              <div className="text-red-400">Error al cargar planes: {String(error)}</div>
            </CardContent>
          </Card>
        ) : filteredPlans.length === 0 ? (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="pt-6 text-center py-12">
              <div className="text-slate-400 mb-4">
                {plans.length === 0 
                  ? 'No tienes planes de entrenamiento. Crea uno nuevo para comenzar.'
                  : 'No se encontraron planes con los filtros seleccionados.'}
              </div>
              {plans.length === 0 && (
                <Button
                  onClick={handleNewPlanClick}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4" />
                  Crear Primer Plan
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPlans.map((plan) => {
              const progress = (plan.current_week / plan.total_weeks) * 100;
              const weeksRemaining = plan.total_weeks - plan.current_week;
              const goalDate = new Date(plan.goal_date);
              const createdDate = new Date(plan.created_at);

              return (
                <Card
                  key={plan.plan_id}
                  className="bg-slate-800/50 border-slate-700 hover:border-slate-600 transition-colors"
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div 
                        className="flex-1 cursor-pointer"
                        onClick={() => {
                          // Fetch full plan and show detail
                          apiClient.client.get(`/api/v1/training-plans/${plan.plan_id}`)
                            .then(res => setCreatedPlan(res.data.plan))
                            .catch(console.error);
                        }}
                      >
                        <CardTitle className="text-white text-xl mb-2">
                          {plan.plan_name}
                        </CardTitle>
                        <Badge className={getStatusColor(plan.status)}>
                          {getStatusLabel(plan.status)}
                        </Badge>
                      </div>
                      <button
                        onClick={async (e) => {
                          e.stopPropagation();
                          if (confirm('¿Estás seguro de que quieres eliminar este plan? Esta acción no se puede deshacer.')) {
                            try {
                              console.log(`[TrainingPlans] Deleting plan: ${plan.plan_id} (${plan.plan_name})`);
                              
                              // Use the dedicated method that handles errors properly
                              // plan_id is already a string, no need to parse
                              await apiClient.deleteTrainingPlan(plan.plan_id);
                              
                              console.log('[TrainingPlans] DELETE API call succeeded, refreshing cache...');
                              
                              // Immediately update the UI optimistically
                              queryClient.setQueryData(['training-plans'], (oldData: PlanSummary[] | undefined) => {
                                if (!oldData) return [];
                                const filtered = oldData.filter(p => p.plan_id !== plan.plan_id);
                                console.log(`[TrainingPlans] Updated cache: ${oldData.length} -> ${filtered.length} plans`);
                                return filtered;
                              });
                              
                              // Force refetch from server to ensure consistency
                              await queryClient.refetchQueries({ 
                                queryKey: ['training-plans'],
                                type: 'active'
                              });
                              
                              console.log('[TrainingPlans] Plan deleted and cache refreshed successfully');
                            } catch (error: any) {
                              console.error('[TrainingPlans] Error deleting plan:', error);
                              const errorMessage = error?.response?.data?.detail || error?.message || 'Error desconocido';
                              alert(`Error al eliminar el plan: ${errorMessage}`);
                              
                              // Refresh to get current state from server
                              queryClient.refetchQueries({ queryKey: ['training-plans'] });
                            }
                          }
                        }}
                        className="text-red-400 hover:text-red-300 p-1"
                        title="Eliminar plan"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Goal Info */}
                      <div className="flex items-center gap-2 text-slate-400 text-sm">
                        <Target className="h-4 w-4" />
                        <span>{getGoalTypeLabel(plan.goal_type)}</span>
                      </div>

                      {/* Dates */}
                      <div className="flex items-center gap-2 text-slate-400 text-sm">
                        <Calendar className="h-4 w-4" />
                        <span>Objetivo: {format(goalDate, 'dd MMM yyyy', { locale: es })}</span>
                      </div>

                      {/* Progress */}
                      <div>
                        <div className="flex items-center justify-between text-sm mb-2">
                          <span className="text-slate-400">Progreso</span>
                          <span className="text-white font-semibold">
                            Semana {plan.current_week}/{plan.total_weeks}
                          </span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{ width: `${Math.min(progress, 100)}%` }}
                          />
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          {weeksRemaining > 0 
                            ? `${weeksRemaining} semana${weeksRemaining > 1 ? 's' : ''} restante${weeksRemaining > 1 ? 's' : ''}`
                            : 'Plan completado'}
                        </div>
                      </div>

                      {/* Created Date */}
                      <div className="text-xs text-slate-500">
                        Creado {formatDistanceToNow(createdDate, { addSuffix: true, locale: es })}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Modal de advertencia de sincronización */}
        <Dialog open={showSyncModal} onOpenChange={setShowSyncModal}>
          <DialogContent className="bg-gradient-to-br from-slate-800 via-slate-800 to-slate-900 border-2 border-blue-500/30 text-white max-w-2xl p-0 shadow-2xl">
            <DialogClose 
              onClick={() => setShowSyncModal(false)}
              className="text-slate-400 hover:text-white transition-colors z-10"
            />
            
            <div className="relative overflow-hidden">
              {/* Decorative gradient background */}
              <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-blue-500 via-cyan-500 to-blue-500"></div>
              
              <DialogHeader className="px-6 pt-6 pb-4 border-b border-slate-700/50">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center border border-blue-500/30">
                    <span className="text-2xl">💡</span>
                  </div>
                  <div className="flex-1">
                    <DialogTitle className="text-2xl font-bold text-white mb-2">
                      Sincroniza primero tus entrenamientos de Garmin
                    </DialogTitle>
                    <DialogDescription className="text-slate-300 text-base leading-relaxed">
                      Para generar un plan de entrenamiento <strong className="text-blue-300 font-semibold">altamente personalizado</strong>, es muy recomendable sincronizar primero tus entrenamientos de Garmin.
                    </DialogDescription>
                  </div>
                </div>
              </DialogHeader>
              
              <div className="px-6 py-5 space-y-5">
                <div>
                  <p className="text-slate-200 font-medium mb-3 text-sm">
                    Esto permite que el sistema:
                  </p>
                  <ul className="space-y-2.5">
                    {[
                      "Analice tu historial de entrenamientos y rendimiento real",
                      "Calcule tu ritmo umbral y zonas de frecuencia cardíaca precisas",
                      "Adapte el volumen y la intensidad a tu nivel actual",
                      "Considere tu fatiga y recuperación basada en métricas reales (HRV, Body Battery)",
                      "Genere un plan que se ajuste perfectamente a tu progreso histórico"
                    ].map((benefit, idx) => (
                      <li key={idx} className="flex items-start gap-3 text-sm text-slate-300">
                        <div className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mt-0.5 border border-blue-500/30">
                          <div className="w-1.5 h-1.5 rounded-full bg-blue-400"></div>
                        </div>
                        <span className="flex-1 leading-relaxed">{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div className="bg-gradient-to-r from-blue-900/40 via-cyan-900/30 to-blue-900/40 border border-blue-600/40 rounded-lg p-4 mt-4 backdrop-blur-sm">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 text-blue-300 text-lg">💡</div>
                    <p className="text-sm text-blue-100 leading-relaxed">
                      <strong className="font-semibold text-blue-200">Tip:</strong> La sincronización importa hasta 2 años de entrenamientos históricos en la primera vez, lo que proporciona un contexto completo para tu plan personalizado.
                    </p>
                  </div>
                </div>
              </div>

              <DialogFooter className="px-6 py-4 border-t border-slate-700/50 bg-slate-800/50 flex gap-3">
                <Button
                  onClick={() => {
                    setShowSyncModal(false);
                    router.push('/garmin');
                  }}
                  className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold flex-1 py-2.5 shadow-lg shadow-blue-500/25 transition-all hover:scale-[1.02]"
                >
                  <span className="mr-2">🔗</span>
                  Ir a Sincronizar Garmin
                </Button>
                <Button
                  onClick={() => {
                    setShowSyncModal(false);
                    setShowForm(true);
                  }}
                  variant="outline"
                  className="border-2 border-slate-600 text-slate-300 hover:bg-slate-700 hover:border-slate-500 flex-1 py-2.5 font-medium transition-all hover:scale-[1.02]"
                >
                  Continuar sin sincronizar
                </Button>
              </DialogFooter>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
