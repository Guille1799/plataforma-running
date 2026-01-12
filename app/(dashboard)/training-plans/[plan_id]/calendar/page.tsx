'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import { PlanCalendar } from '@/components/training-plan/plan-calendar';
import { ArrowLeft } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function TrainingPlanCalendarPage() {
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

  const handleDayClick = (date: Date, workout: any) => {
    if (workout) {
      // TODO: Show workout detail modal or navigate to workout detail
      console.log('Workout clicked:', workout);
    }
  };

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

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Button
            onClick={() => router.back()}
            variant="outline"
            className="mb-4 border-slate-700"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
          <h1 className="text-3xl font-bold text-white mb-2">
            {planData.plan_name}
          </h1>
          <p className="text-slate-400">
            Vista de calendario del plan de entrenamiento
          </p>
        </div>

        {/* Calendar */}
        <PlanCalendar plan={planData} onDayClick={handleDayClick} />
      </div>
    </div>
  );
}
