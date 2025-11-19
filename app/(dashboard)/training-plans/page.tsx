'use client';

import { TrainingPlanFormV2 } from '../dashboard/training-plan-form-v2';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRouter } from 'next/navigation';

export default function TrainingPlansPage() {
  const router = useRouter();

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Planes de Entrenamiento 📋
          </h1>
          <p className="text-slate-400">
            Crea un plan personalizado con inteligencia artificial adaptado a tus objetivos y disponibilidad
          </p>
        </div>

        {/* Form Container */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-2xl">Nuevo Plan de Entrenamiento</CardTitle>
          </CardHeader>
          <CardContent>
            <TrainingPlanFormV2
              onPlanCreated={(plan) => {
                // Redirige al dashboard cuando se crea el plan
                router.push('/dashboard?tab=training-plan');
              }}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
