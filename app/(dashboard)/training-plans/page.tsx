'use client';

import { TrainingPlanFormV2 } from '../dashboard/training-plan-form-v2';
import { TrainingPlanDetail } from '../dashboard/training-plan-detail';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useState } from 'react';

export default function TrainingPlansPage() {
  const [createdPlan, setCreatedPlan] = useState<any>(null);

  if (createdPlan) {
    return (
      <div className="p-8">
        <div className="max-w-6xl mx-auto">
          <button
            onClick={() => setCreatedPlan(null)}
            className="mb-6 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm"
          >
            ← Crear otro plan
          </button>
          <TrainingPlanDetail plan={createdPlan} />
        </div>
      </div>
    );
  }

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
                // Show the created plan instead of redirecting
                setCreatedPlan(plan);
              }}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
