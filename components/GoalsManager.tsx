'use client';

/**
 * GoalsManager.tsx - Component for managing user goals
 */
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { Goal } from '@/lib/types';

interface GoalsManagerProps {
  goals: Goal[];
  onAddGoal: (goal: Goal) => void;
  onRemoveGoal: (index: number) => void;
  onUpdateGoal: (index: number, goal: Goal) => void;
}

export function GoalsManager({ goals, onAddGoal, onRemoveGoal, onUpdateGoal }: GoalsManagerProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [newGoal, setNewGoal] = useState<Goal>({
    type: 'race',
    target: '',
    deadline: '',
    description: '',
  });

  const goalTypes = [
    { value: 'race', label: '🏁 Carrera', icon: '🏁' },
    { value: 'distance', label: '📏 Distancia', icon: '📏' },
    { value: 'pace', label: '⚡ Pace', icon: '⚡' },
    { value: 'weight', label: '⚖️ Peso', icon: '⚖️' },
    { value: 'consistency', label: '📅 Consistencia', icon: '📅' },
  ];

  const handleAddClick = () => {
    if (!newGoal.target || !newGoal.deadline) return;
    
    onAddGoal(newGoal);
    setNewGoal({
      type: 'race',
      target: '',
      deadline: '',
      description: '',
    });
    setIsAdding(false);
  };

  const getGoalIcon = (type: string) => {
    return goalTypes.find(gt => gt.value === type)?.icon || '🎯';
  };

  const formatDeadline = (deadline: string) => {
    return new Date(deadline).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="text-white">Mis Objetivos 🎯</span>
          <Button
            onClick={() => setIsAdding(!isAdding)}
            size="sm"
            variant="outline"
            className="border-blue-500 text-blue-400 hover:bg-blue-500/20"
          >
            {isAdding ? 'Cancelar' : '+ Agregar Objetivo'}
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Add Goal Form */}
        {isAdding && (
          <div className="p-4 bg-slate-700/50 rounded-lg border border-slate-600 space-y-3">
            <div>
              <Label className="text-slate-300 text-sm">Tipo de Objetivo</Label>
              <select
                value={newGoal.type}
                onChange={(e) => setNewGoal({ ...newGoal, type: e.target.value as any })}
                className="w-full mt-1 px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                {goalTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Label className="text-slate-300 text-sm">Objetivo / Target</Label>
              <Input
                value={newGoal.target}
                onChange={(e) => setNewGoal({ ...newGoal, target: e.target.value })}
                placeholder="ej: 10K en 45 minutos"
                className="mt-1 bg-slate-800 border-slate-600 text-white"
              />
            </div>

            <div>
              <Label className="text-slate-300 text-sm">Fecha Límite</Label>
              <Input
                type="date"
                value={newGoal.deadline}
                onChange={(e) => setNewGoal({ ...newGoal, deadline: e.target.value })}
                className="mt-1 bg-slate-800 border-slate-600 text-white"
              />
            </div>

            <div>
              <Label className="text-slate-300 text-sm">Descripción (Opcional)</Label>
              <Input
                value={newGoal.description}
                onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
                placeholder="Detalles adicionales..."
                className="mt-1 bg-slate-800 border-slate-600 text-white"
              />
            </div>

            <Button
              onClick={handleAddClick}
              className="w-full bg-blue-600 hover:bg-blue-700"
              disabled={!newGoal.target || !newGoal.deadline}
            >
              Guardar Objetivo
            </Button>
          </div>
        )}

        {/* Goals List */}
        {goals.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-5xl mb-3">🎯</div>
            <p className="text-slate-400">No tienes objetivos aún</p>
            <p className="text-sm text-slate-500 mt-1">
              Agrega tu primer objetivo para empezar a trackear tu progreso
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {goals.map((goal, index) => (
              <div
                key={index}
                className="p-4 bg-slate-700/30 border border-slate-600 rounded-lg hover:border-slate-500 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{getGoalIcon(goal.type)}</span>
                      <h4 className="text-white font-semibold">{goal.target}</h4>
                    </div>
                    
                    {goal.description && (
                      <p className="text-sm text-slate-400 mb-2">{goal.description}</p>
                    )}
                    
                    <div className="flex items-center gap-4 text-xs text-slate-400">
                      <span className="flex items-center gap-1">
                        <span>📅</span>
                        {goal.deadline ? formatDeadline(goal.deadline) : 'Sin fecha'}
                      </span>
                      <span className="px-2 py-1 bg-slate-800 rounded-full">
                        {goalTypes.find(gt => gt.value === goal.type)?.label}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => onRemoveGoal(index)}
                    className="ml-4 p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                    title="Eliminar objetivo"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
