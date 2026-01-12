'use client';

/**
 * Onboarding Page - Device selection, goals, and personalization
 */
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ChevronRight, Watch, Smartphone, Zap, Heart, Brain } from 'lucide-react';

type Step = 'language' | 'device' | 'usecase' | 'style' | 'confirm';

interface OnboardingData {
  primary_device: string;
  use_case: string;
  coach_style_preference: string;
  language: string;
  enable_notifications: boolean;
  integration_sources: string[];
}

// Translations
const translations = {
  es: {
    progress: 'Progreso de Configuración',
    language: {
      title: 'Idioma Preferido',
      description: 'Elige el idioma de la interfaz'
    },
    device: {
      title: '¿Qué dispositivo usas?',
      description: 'Selecciona tu dispositivo principal de running/fitness'
    },
    usecase: {
      title: '¿Cuál es tu objetivo principal?',
      description: 'Esto ayuda a personalizar tu experiencia de coaching'
    },
    style: {
      title: '¿Cómo debe ser tu coach?',
      description: 'Elige tu estilo de coaching preferido'
    },
    confirm: {
      title: '✅ ¡Casi terminamos!',
      description: 'Revisa tu configuración y comienza a entrenar',
      device: 'Dispositivo',
      goal: 'Objetivo',
      coachStyle: 'Estilo de Coach',
      language: 'Idioma',
      back: '← Atrás',
      start: '¡Comenzar Entrenamiento! 🚀',
      settingUp: 'Configurando...'
    },
    notifications: 'Activar notificaciones',
    back: '← Atrás',
    devices: {
      garmin: {
        name: 'Garmin',
        description: 'Relojes Garmin con métricas avanzadas (HRV, Body Battery)',
        features: ['Seguimiento HRV', 'Body Battery', 'Carga de entrenamiento', 'Análisis de sueño']
      },
      xiaomi: {
        name: 'Xiaomi / Amazfit',
        description: 'Wearables Xiaomi y Amazfit',
        features: ['Frecuencia cardíaca', 'Seguimiento de sueño', 'Monitoreo de actividad', 'Nivel de estrés']
      },
      apple: {
        name: 'Apple Health',
        description: 'Datos de salud de Apple Watch e iPhone',
        features: ['Variabilidad de frecuencia cardíaca', 'Entrenamientos', 'Sueño', 'Anillos de actividad']
      },
      strava: {
        name: 'Strava',
        description: 'Seguimiento GPS y compartir entrenamientos',
        features: ['Rutas GPS', 'PRs de segmentos', 'Funciones sociales', 'Kudos']
      },
      manual: {
        name: 'Entrada Manual',
        description: 'Registra entrenamientos y métricas manualmente',
        features: ['Control total', 'Formato flexible', 'Métricas personalizadas', 'No requiere sincronización']
      }
    },
    usecases: {
      fitness_tracker: {
        name: 'Monitor de Actividad',
        description: 'Monitorea la actividad diaria y salud general'
      },
      training_coach: {
        name: 'Coach de Entrenamiento',
        description: 'Obtén planes de entrenamiento y coaching personalizados'
      },
      race_prep: {
        name: 'Preparación para Carrera',
        description: 'Entrena para una carrera o evento específico'
      },
      general_health: {
        name: 'Salud General',
        description: 'Rastrea métricas de salud y bienestar'
      }
    },
    coachStyles: {
      motivator: {
        name: '🏃 Motivador',
        description: 'Estilo de coaching energético y alentador'
      },
      technical: {
        name: '📊 Técnico',
        description: 'Enfoque analítico basado en datos'
      },
      balanced: {
        name: '⚖️ Balanceado',
        description: 'Mezcla de motivación y análisis técnico'
      },
      custom: {
        name: '🎯 Personalizado',
        description: 'Déjame personalizarlo yo mismo (configurar en Perfil)'
      }
    },
    error: 'Error en el onboarding. Por favor, inténtalo de nuevo.'
  },
  en: {
    progress: 'Setup Progress',
    language: {
      title: 'Preferred Language',
      description: 'Choose your interface language'
    },
    device: {
      title: 'Which device do you use?',
      description: 'Select your primary running/fitness device'
    },
    usecase: {
      title: "What's your main goal?",
      description: 'This helps personalize your coaching experience'
    },
    style: {
      title: 'How should your coach be?',
      description: 'Choose your preferred coaching style'
    },
    confirm: {
      title: '✅ Almost there!',
      description: 'Review your settings and start training',
      device: 'Device',
      goal: 'Goal',
      coachStyle: 'Coach Style',
      language: 'Language',
      back: '← Back',
      start: 'Start Training! 🚀',
      settingUp: 'Setting up...'
    },
    notifications: 'Enable notifications',
    back: '← Back',
    devices: {
      garmin: {
        name: 'Garmin',
        description: 'Garmin watches with advanced metrics (HRV, Body Battery)',
        features: ['HRV tracking', 'Body Battery', 'Training load', 'Sleep analysis']
      },
      xiaomi: {
        name: 'Xiaomi / Amazfit',
        description: 'Xiaomi and Amazfit wearables',
        features: ['Heart rate', 'Sleep tracking', 'Activity monitoring', 'Stress level']
      },
      apple: {
        name: 'Apple Health',
        description: 'Apple Watch and iPhone health data',
        features: ['Heart rate variability', 'Workouts', 'Sleep', 'Activity rings']
      },
      strava: {
        name: 'Strava',
        description: 'GPS tracking and workout sharing',
        features: ['GPS routes', 'Segment PRs', 'Social features', 'Kudos']
      },
      manual: {
        name: 'Manual Entry',
        description: 'Log workouts and metrics manually',
        features: ['Full control', 'Flexible format', 'Custom metrics', 'No sync needed']
      }
    },
    usecases: {
      fitness_tracker: {
        name: 'Fitness Tracker',
        description: 'Monitor daily activity and general health'
      },
      training_coach: {
        name: 'Training Coach',
        description: 'Get personalized training plans and coaching'
      },
      race_prep: {
        name: 'Race Prep',
        description: 'Train for a specific race or event'
      },
      general_health: {
        name: 'General Health',
        description: 'Track health and wellness metrics'
      }
    },
    coachStyles: {
      motivator: {
        name: '🏃 Motivator',
        description: 'Energetic and encouraging coaching style'
      },
      technical: {
        name: '📊 Technical',
        description: 'Data-driven and analytical approach'
      },
      balanced: {
        name: '⚖️ Balanced',
        description: 'Mix of motivation and technical analysis'
      },
      custom: {
        name: '🎯 Custom',
        description: 'Let me personalize this myself (configure in Profile)'
      }
    },
    error: 'Onboarding failed. Please try again.'
  }
};

const DEVICES = [
  { id: 'garmin', icon: Watch },
  { id: 'xiaomi', icon: Smartphone },
  { id: 'apple', icon: Heart },
  { id: 'strava', icon: Zap },
  { id: 'manual', icon: Brain }
];

const USE_CASES = [
  { id: 'fitness_tracker' },
  { id: 'training_coach' },
  { id: 'race_prep' },
  { id: 'general_health' }
];

const COACH_STYLES = [
  { id: 'motivator' },
  { id: 'technical' },
  { id: 'balanced' },
  { id: 'custom' }
];

const LANGUAGES = [
  { id: 'es', name: 'Español' },
  { id: 'en', name: 'English' },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<Step>('language');
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState<OnboardingData>({
    primary_device: '',
    use_case: '',
    coach_style_preference: '',
    language: 'es',
    enable_notifications: true,
    integration_sources: []
  });

  const handleLanguageSelect = (langId: string) => {
    setData({ ...data, language: langId });
    setCurrentStep('device');
  };

  const handleDeviceSelect = (deviceId: string) => {
    setData({ ...data, primary_device: deviceId });
    setCurrentStep('usecase');
  };

  const handleUseCaseSelect = (useCaseId: string) => {
    setData({ ...data, use_case: useCaseId });
    setCurrentStep('style');
  };

  const handleStyleSelect = (styleId: string) => {
    setData({ ...data, coach_style_preference: styleId });
    setCurrentStep('confirm');
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.completeOnboarding(data);
      if (response.success) {
        // Refrescar el perfil del usuario para que se actualice el primary_device
        window.location.href = '/dashboard'; // Usar window.location para forzar recarga completa
      }
    } catch (error) {
      console.error('Onboarding failed:', error);
      const t = translations[data.language as 'es' | 'en'] || translations.es;
      alert(t.error);
    } finally {
      setIsLoading(false);
    }
  };

  const getProgress = () => {
    const steps = ['language', 'device', 'usecase', 'style', 'confirm'];
    return ((steps.indexOf(currentStep) + 1) / steps.length) * 100;
  };

  const t = translations[data.language as 'es' | 'en'] || translations.es;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-slate-400 mb-2">
            <span>{t.progress}</span>
            <span>{Math.round(getProgress())}%</span>
          </div>
          <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-300"
              style={{ width: `${getProgress()}%` }}
            />
          </div>
        </div>

        {/* Language Selection */}
        {currentStep === 'language' && (
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle>{t.language.title}</CardTitle>
              <CardDescription>{t.language.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang.id}
                    onClick={() => handleLanguageSelect(lang.id)}
                    className={`p-4 rounded-lg border-2 transition-all font-semibold ${
                      data.language === lang.id
                        ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                        : 'border-slate-600 hover:border-slate-500 bg-slate-900/30 hover:bg-slate-900/50 text-white'
                    }`}
                  >
                    {lang.name}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Device Selection */}
        {currentStep === 'device' && (
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle>{t.device.title}</CardTitle>
              <CardDescription>{t.device.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {DEVICES.map((device) => {
                const Icon = device.icon;
                const deviceInfo = t.devices[device.id as keyof typeof t.devices];
                return (
                  <button
                    key={device.id}
                    onClick={() => handleDeviceSelect(device.id)}
                    className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                      data.primary_device === device.id
                        ? 'border-blue-500 bg-blue-500/10'
                        : 'border-slate-600 hover:border-slate-500 bg-slate-900/30 hover:bg-slate-900/50'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <Icon className="h-6 w-6 text-blue-400 mt-1" />
                      <div className="flex-1">
                        <h3 className="font-semibold text-white">{deviceInfo.name}</h3>
                        <p className="text-sm text-slate-400">{deviceInfo.description}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {deviceInfo.features.map((feature) => (
                            <Badge key={feature} variant="outline" className="text-xs">
                              {feature}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <ChevronRight className="h-5 w-5 text-slate-500 mt-1" />
                    </div>
                  </button>
                );
              })}
              <button
                onClick={() => setCurrentStep('language')}
                className="w-full mt-4 px-4 py-2 rounded-lg border border-slate-600 text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
              >
                {t.back}
              </button>
            </CardContent>
          </Card>
        )}

        {/* Use Case Selection */}
        {currentStep === 'usecase' && (
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle>{t.usecase.title}</CardTitle>
              <CardDescription>{t.usecase.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {USE_CASES.map((useCase) => {
                const useCaseInfo = t.usecases[useCase.id as keyof typeof t.usecases];
                return (
                  <button
                    key={useCase.id}
                    onClick={() => handleUseCaseSelect(useCase.id)}
                    className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                      data.use_case === useCase.id
                        ? 'border-blue-500 bg-blue-500/10'
                        : 'border-slate-600 hover:border-slate-500 bg-slate-900/30 hover:bg-slate-900/50'
                    }`}
                  >
                    <h3 className="font-semibold text-white">{useCaseInfo.name}</h3>
                    <p className="text-sm text-slate-400 mt-1">{useCaseInfo.description}</p>
                    <ChevronRight className="h-5 w-5 text-slate-500 mt-2 float-right" />
                  </button>
                );
              })}
              <button
                onClick={() => setCurrentStep('device')}
                className="w-full mt-4 px-4 py-2 rounded-lg border border-slate-600 text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
              >
                {t.back}
              </button>
            </CardContent>
          </Card>
        )}

        {/* Coach Style Selection */}
        {currentStep === 'style' && (
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle>{t.style.title}</CardTitle>
              <CardDescription>{t.style.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {COACH_STYLES.map((style) => {
                const styleInfo = t.coachStyles[style.id as keyof typeof t.coachStyles];
                return (
                  <button
                    key={style.id}
                    onClick={() => handleStyleSelect(style.id)}
                    className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                      data.coach_style_preference === style.id
                        ? 'border-blue-500 bg-blue-500/10'
                        : 'border-slate-600 hover:border-slate-500 bg-slate-900/30 hover:bg-slate-900/50'
                    }`}
                  >
                    <h3 className="font-semibold text-white">{styleInfo.name}</h3>
                    <p className="text-sm text-slate-400 mt-1">{styleInfo.description}</p>
                  </button>
                );
              })}

              {/* Notifications Toggle */}
              <div className="mt-4 p-4 bg-slate-900/30 rounded-lg border border-slate-600">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">{t.notifications}</span>
                  <button
                    onClick={() => setData({ ...data, enable_notifications: !data.enable_notifications })}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      data.enable_notifications
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-600 text-slate-300'
                    }`}
                  >
                    {data.enable_notifications ? 'ON' : 'OFF'}
                  </button>
                </div>
              </div>

              <button
                onClick={() => setCurrentStep('usecase')}
                className="w-full mt-4 px-4 py-2 rounded-lg border border-slate-600 text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
              >
                {t.back}
              </button>
            </CardContent>
          </Card>
        )}

        {/* Confirmation */}
        {currentStep === 'confirm' && (
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle>{t.confirm.title}</CardTitle>
              <CardDescription>{t.confirm.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3 p-4 bg-slate-900/30 rounded-lg">
                <div className="flex justify-between">
                  <span className="text-slate-400">{t.confirm.device}:</span>
                  <span className="text-white font-semibold capitalize">{t.devices[data.primary_device as keyof typeof t.devices]?.name || data.primary_device}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">{t.confirm.goal}:</span>
                  <span className="text-white font-semibold capitalize">{t.usecases[data.use_case as keyof typeof t.usecases]?.name || data.use_case.replace('_', ' ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">{t.confirm.coachStyle}:</span>
                  <span className="text-white font-semibold capitalize">{t.coachStyles[data.coach_style_preference as keyof typeof t.coachStyles]?.name || data.coach_style_preference}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">{t.confirm.language}:</span>
                  <span className="text-white font-semibold uppercase">{data.language === 'es' ? 'Español' : 'English'}</span>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setCurrentStep('style')}
                  className="flex-1 px-4 py-3 rounded-lg border border-slate-600 text-slate-400 hover:text-white hover:border-slate-500 transition-colors font-medium"
                >
                  {t.confirm.back}
                </button>
                <Button
                  onClick={handleSubmit}
                  disabled={isLoading}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold py-3 rounded-lg"
                >
                  {isLoading ? t.confirm.settingUp : t.confirm.start}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
