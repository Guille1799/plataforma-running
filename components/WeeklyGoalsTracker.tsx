'use client';

/**
 * WeeklyGoalsTracker Component
 * Tracks and displays weekly training goals and progress
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { CheckCircle2, Circle, Target, AlertCircle, Plus } from 'lucide-react';

interface Goal {
  id: string;
  name: string;
  target: number;
  current: number;
  unit: string;
  completed: boolean;
  dueDate: string;
}

export function WeeklyGoalsTracker() {
  const [goals, setGoals] = useState<Goal[]>([
    {
      id: '1',
      name: 'Weekly Distance',
      target: 30,
      current: 18,
      unit: 'km',
      completed: false,
      dueDate: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    },
    {
      id: '2',
      name: 'Running Sessions',
      target: 4,
      current: 2,
      unit: 'sessions',
      completed: false,
      dueDate: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    },
    {
      id: '3',
      name: 'Speed Work',
      target: 2,
      current: 1,
      unit: 'sessions',
      completed: false,
      dueDate: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    },
    {
      id: '4',
      name: 'Long Run',
      target: 1,
      current: 0,
      unit: 'run',
      completed: false,
      dueDate: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    },
  ]);

  const queryClient = useQueryClient();

  const toggleGoal = (goalId: string) => {
    setGoals(goals.map(g => 
      g.id === goalId 
        ? { ...g, completed: !g.completed }
        : g
    ));
  };

  const updateProgress = (goalId: string, newValue: number) => {
    setGoals(goals.map(g =>
      g.id === goalId
        ? { ...g, current: Math.min(newValue, g.target) }
        : g
    ));
  };

  // Calculate overall progress
  const totalProgress = goals.length > 0
    ? (goals.reduce((sum, g) => sum + (g.current / g.target), 0) / goals.length * 100).toFixed(0)
    : 0;

  const completedGoals = goals.filter(g => g.completed || g.current >= g.target).length;

  return (
    <div className="space-y-6">
      {/* Progress Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-slate-800/50 backdrop-blur border-slate-700 border-l-4 border-l-blue-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <Target className="h-4 w-4" />
              Overall Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-400">
              {totalProgress}%
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2 mt-3">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${totalProgress}%` }}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 backdrop-blur border-slate-700 border-l-4 border-l-green-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" />
              Goals Completed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-400">
              {completedGoals}/{goals.length}
            </div>
            <p className="text-xs text-slate-500 mt-1">this week</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 backdrop-blur border-slate-700 border-l-4 border-l-purple-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              Days Remaining
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-400">
              4
            </div>
            <p className="text-xs text-slate-500 mt-1">to complete goals</p>
          </CardContent>
        </Card>
      </div>

      {/* Goals List */}
      <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Weekly Goals</span>
            <button className="flex items-center gap-2 px-3 py-1 text-sm bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
              <Plus className="h-4 w-4" />
              Add Goal
            </button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {goals.map((goal) => {
            const progress = (goal.current / goal.target) * 100;
            const isCompleted = goal.completed || goal.current >= goal.target;

            return (
              <div 
                key={goal.id}
                className="p-4 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start gap-3 flex-1">
                    <button
                      onClick={() => toggleGoal(goal.id)}
                      className="mt-1 transition-colors"
                    >
                      {isCompleted ? (
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                      ) : (
                        <Circle className="h-5 w-5 text-slate-600 hover:text-slate-400" />
                      )}
                    </button>
                    <div>
                      <h3 className={`font-medium ${isCompleted ? 'text-slate-500 line-through' : 'text-white'}`}>
                        {goal.name}
                      </h3>
                      <p className="text-xs text-slate-500">
                        Due: {new Date(goal.dueDate).toLocaleDateString('es-ES', { 
                          weekday: 'short', 
                          month: 'short', 
                          day: 'numeric' 
                        })}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-white">
                      {goal.current}/{goal.target} {goal.unit}
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-slate-700 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        isCompleted 
                          ? 'bg-green-500' 
                          : progress > 75 
                          ? 'bg-blue-500' 
                          : progress > 50 
                          ? 'bg-yellow-500' 
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(progress, 100)}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-slate-400 min-w-[40px] text-right">
                    {progress.toFixed(0)}%
                  </span>
                </div>

                {/* Progress Input */}
                <div className="mt-3 flex items-center gap-2">
                  <input
                    type="range"
                    min="0"
                    max={goal.target}
                    value={goal.current}
                    onChange={(e) => updateProgress(goal.id, parseFloat(e.target.value))}
                    disabled={isCompleted}
                    className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer opacity-70 hover:opacity-100 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <input
                    type="number"
                    min="0"
                    max={goal.target}
                    value={goal.current}
                    onChange={(e) => updateProgress(goal.id, parseFloat(e.target.value))}
                    disabled={isCompleted}
                    className="w-16 px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-sm text-center disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}
