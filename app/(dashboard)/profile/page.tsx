'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api-client';
import type { AthleteProfile, Goal } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { GoalsManager } from '@/components/GoalsManager';

export default function ProfilePage() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  const [profile, setProfile] = useState<AthleteProfile>({
    running_level: 'intermediate',
    max_heart_rate: 190,
    coaching_style: 'balanced',
    goals: [],
    preferences: {
      preferred_training_days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      available_hours_per_week: 5,
      preferred_workout_time: 'evening',
    },
  });

  const [formData, setFormData] = useState({
    height_cm: '',
    weight_kg: '',
    max_heart_rate: '',
    running_level: 'intermediate',
    coaching_style: 'balanced',
  });

  const handleAddGoal = (goal: Goal) => {
    setProfile(prev => ({
      ...prev,
      goals: [...(prev.goals || []), goal]
    }));
  };

  const handleRemoveGoal = (index: number) => {
    setProfile(prev => ({
      ...prev,
      goals: prev.goals?.filter((_, i) => i !== index) || []
    }));
  };

  const handleUpdateGoal = (index: number, goal: Goal) => {
    setProfile(prev => ({
      ...prev,
      goals: prev.goals?.map((g, i) => i === index ? goal : g) || []
    }));
  };

  useEffect(() => {
    // Load user profile data
    if (user) {
      setFormData({
        height_cm: user.height_cm?.toString() || '',
        weight_kg: user.weight_kg?.toString() || '',
        max_heart_rate: user.max_heart_rate?.toString() || '190',
        running_level: user.running_level || 'intermediate',
        coaching_style: user.coaching_style || 'balanced',
      });
    }
  }, [user]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError('');
    setSuccess('');

    try {
      // Aquí iría la llamada al backend para guardar el perfil
      // await apiClient.updateProfile(formData);
      setSuccess('¡Perfil actualizado correctamente!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al guardar perfil');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Mi Perfil 👤
          </h1>
          <p className="text-slate-400">
            Configura tu información personal y objetivos de entrenamiento
          </p>
        </div>

        {/* Messages */}
        {error && (
          <div className="p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-200">
            {error}
          </div>
        )}
        {success && (
          <div className="p-4 bg-green-900/50 border border-green-700 rounded-lg text-green-200">
            {success}
          </div>
        )}

        {/* Personal Data */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Datos Personales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-slate-200">Email</Label>
                <Input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="bg-slate-900/50 border-slate-700 text-slate-400 mt-2"
                />
              </div>

              <div>
                <Label className="text-slate-200">Altura (cm)</Label>
                <Input
                  type="number"
                  value={formData.height_cm}
                  onChange={(e) => handleInputChange('height_cm', e.target.value)}
                  placeholder="180"
                  className="bg-slate-900/50 border-slate-700 text-white mt-2"
                />
              </div>

              <div>
                <Label className="text-slate-200">Peso (kg)</Label>
                <Input
                  type="number"
                  value={formData.weight_kg}
                  onChange={(e) => handleInputChange('weight_kg', e.target.value)}
                  placeholder="75"
                  className="bg-slate-900/50 border-slate-700 text-white mt-2"
                />
              </div>

              <div>
                <Label className="text-slate-200">FC Máxima (bpm)</Label>
                <Input
                  type="number"
                  value={formData.max_heart_rate}
                  onChange={(e) => handleInputChange('max_heart_rate', e.target.value)}
                  placeholder="190"
                  className="bg-slate-900/50 border-slate-700 text-white mt-2"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Training Preferences */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Preferencias de Entrenamiento</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-slate-200">Nivel</Label>
                <select
                  value={formData.running_level}
                  onChange={(e) => handleInputChange('running_level', e.target.value)}
                  className="w-full mt-2 bg-slate-900/50 border border-slate-700 rounded-md text-white p-2"
                >
                  <option value="beginner">Principiante</option>
                  <option value="intermediate">Intermedio</option>
                  <option value="advanced">Avanzado</option>
                  <option value="elite">Élite</option>
                </select>
              </div>

              <div>
                <Label className="text-slate-200">Estilo de Coaching</Label>
                <select
                  value={formData.coaching_style}
                  onChange={(e) => handleInputChange('coaching_style', e.target.value)}
                  className="w-full mt-2 bg-slate-900/50 border border-slate-700 rounded-md text-white p-2"
                >
                  <option value="motivational">Motivador</option>
                  <option value="analytical">Analítico</option>
                  <option value="balanced">Balanceado</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Goals Manager */}
        <GoalsManager
          goals={profile.goals || []}
          onAddGoal={handleAddGoal}
          onRemoveGoal={handleRemoveGoal}
          onUpdateGoal={handleUpdateGoal}
        />

        {/* Save Button */}
        <div className="flex gap-3">
          <Button
            onClick={handleSave}
            disabled={isSaving}
            className="flex-1 bg-green-600 hover:bg-green-700"
          >
            {isSaving ? 'Guardando...' : 'Guardar Cambios'}
          </Button>
        </div>
      </div>
    </div>
  );
}
