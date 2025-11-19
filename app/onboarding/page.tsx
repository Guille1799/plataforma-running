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

type Step = 'device' | 'usecase' | 'style' | 'language' | 'confirm';

interface OnboardingData {
  primary_device: string;
  use_case: string;
  coach_style_preference: string;
  language: string;
  enable_notifications: boolean;
  integration_sources: string[];
}

const DEVICES = [
  {
    id: 'garmin',
    name: 'Garmin',
    icon: Watch,
    description: 'Garmin watches with advanced metrics (HRV, Body Battery)',
    features: ['HRV tracking', 'Body Battery', 'Training load', 'Sleep analysis']
  },
  {
    id: 'xiaomi',
    name: 'Xiaomi / Amazfit',
    icon: Smartphone,
    description: 'Xiaomi and Amazfit wearables',
    features: ['Heart rate', 'Sleep tracking', 'Activity monitoring', 'Stress level']
  },
  {
    id: 'apple',
    name: 'Apple Health',
    icon: Heart,
    description: 'Apple Watch and iPhone health data',
    features: ['Heart rate variability', 'Workouts', 'Sleep', 'Activity rings']
  },
  {
    id: 'strava',
    name: 'Strava',
    icon: Zap,
    description: 'GPS tracking and workout sharing',
    features: ['GPS routes', 'Segment PRs', 'Social features', 'Kudos']
  },
  {
    id: 'manual',
    name: 'Manual Entry',
    icon: Brain,
    description: 'Log workouts and metrics manually',
    features: ['Full control', 'Flexible format', 'Custom metrics', 'No sync needed']
  }
];

const USE_CASES = [
  {
    id: 'fitness_tracker',
    name: 'Fitness Tracker',
    description: 'Monitor daily activity and general health'
  },
  {
    id: 'training_coach',
    name: 'Training Coach',
    description: 'Get personalized training plans and coaching'
  },
  {
    id: 'race_prep',
    name: 'Race Prep',
    description: 'Train for a specific race or event'
  },
  {
    id: 'general_health',
    name: 'General Health',
    description: 'Track health and wellness metrics'
  }
];

const COACH_STYLES = [
  {
    id: 'motivator',
    name: '🏃 Motivator',
    description: 'Energetic and encouraging coaching style'
  },
  {
    id: 'technical',
    name: '📊 Technical',
    description: 'Data-driven and analytical approach'
  },
  {
    id: 'balanced',
    name: '⚖️ Balanced',
    description: 'Mix of motivation and technical analysis'
  },
  {
    id: 'custom',
    name: '🎯 Custom',
    description: 'Let me personalize this myself'
  }
];

const LANGUAGES = [
  { id: 'es', name: 'Español' },
  { id: 'en', name: 'English' },
  { id: 'fr', name: 'Français' },
  { id: 'de', name: 'Deutsch' },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<Step>('device');
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState<OnboardingData>({
    primary_device: '',
    use_case: '',
    coach_style_preference: 'balanced',
    language: 'es',
    enable_notifications: true,
    integration_sources: []
  });

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
    setCurrentStep('language');
  };

  const handleLanguageSelect = (langId: string) => {
    setData({ ...data, language: langId });
    setCurrentStep('confirm');
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.completeOnboarding(data);
      if (response.success) {
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Onboarding failed:', error);
      alert('Onboarding failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getProgress = () => {
    const steps = ['device', 'usecase', 'style', 'language', 'confirm'];
    return ((steps.indexOf(currentStep) + 1) / steps.length) * 100;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-slate-400 mb-2">
            <span>Setup Progress</span>
            <span>{Math.round(getProgress())}%</span>
          </div>
          <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-300"
              style={{ width: `${getProgress()}%` }}
            />
          </div>
        </div>

        {/* Device Selection */}
        {currentStep === 'device' && (
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle>Which device do you use?</CardTitle>
              <CardDescription>Select your primary running/fitness device</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {DEVICES.map((device) => {
                const Icon = device.icon;
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
                        <h3 className="font-semibold text-white">{device.name}</h3>
                        <p className="text-sm text-slate-400">{device.description}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {device.features.map((feature) => (
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
            </CardContent>
          </Card>
        )}

        {/* Use Case Selection */}
        {currentStep === 'usecase' && (
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle>What's your main goal?</CardTitle>
              <CardDescription>This helps personalize your coaching experience</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {USE_CASES.map((useCase) => (
                <button
                  key={useCase.id}
                  onClick={() => handleUseCaseSelect(useCase.id)}
                  className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                    data.use_case === useCase.id
                      ? 'border-blue-500 bg-blue-500/10'
                      : 'border-slate-600 hover:border-slate-500 bg-slate-900/30 hover:bg-slate-900/50'
                  }`}
                >
                  <h3 className="font-semibold text-white">{useCase.name}</h3>
                  <p className="text-sm text-slate-400 mt-1">{useCase.description}</p>
                  <ChevronRight className="h-5 w-5 text-slate-500 mt-2 float-right" />
                </button>
              ))}
              <button
                onClick={() => setCurrentStep('device')}
                className="w-full mt-4 px-4 py-2 rounded-lg border border-slate-600 text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
              >
                ← Back
              </button>
            </CardContent>
          </Card>
        )}

        {/* Coach Style Selection */}
        {currentStep === 'style' && (
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle>How should your coach be?</CardTitle>
              <CardDescription>Choose your preferred coaching style</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {COACH_STYLES.map((style) => (
                <button
                  key={style.id}
                  onClick={() => handleStyleSelect(style.id)}
                  className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                    data.coach_style_preference === style.id
                      ? 'border-blue-500 bg-blue-500/10'
                      : 'border-slate-600 hover:border-slate-500 bg-slate-900/30 hover:bg-slate-900/50'
                  }`}
                >
                  <h3 className="font-semibold text-white">{style.name}</h3>
                  <p className="text-sm text-slate-400 mt-1">{style.description}</p>
                </button>
              ))}
              <button
                onClick={() => setCurrentStep('usecase')}
                className="w-full mt-4 px-4 py-2 rounded-lg border border-slate-600 text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
              >
                ← Back
              </button>
            </CardContent>
          </Card>
        )}

        {/* Language Selection */}
        {currentStep === 'language' && (
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle>Preferred Language</CardTitle>
              <CardDescription>Choose your interface language</CardDescription>
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
              
              {/* Notifications Toggle */}
              <div className="mt-6 p-4 bg-slate-900/30 rounded-lg border border-slate-600">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">Enable notifications</span>
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
                onClick={() => setCurrentStep('style')}
                className="w-full mt-4 px-4 py-2 rounded-lg border border-slate-600 text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
              >
                ← Back
              </button>
            </CardContent>
          </Card>
        )}

        {/* Confirmation */}
        {currentStep === 'confirm' && (
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle>✅ Almost there!</CardTitle>
              <CardDescription>Review your settings and start training</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3 p-4 bg-slate-900/30 rounded-lg">
                <div className="flex justify-between">
                  <span className="text-slate-400">Device:</span>
                  <span className="text-white font-semibold capitalize">{data.primary_device}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Goal:</span>
                  <span className="text-white font-semibold capitalize">{data.use_case.replace('_', ' ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Coach Style:</span>
                  <span className="text-white font-semibold capitalize">{data.coach_style_preference}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Language:</span>
                  <span className="text-white font-semibold uppercase">{data.language}</span>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setCurrentStep('language')}
                  className="flex-1 px-4 py-3 rounded-lg border border-slate-600 text-slate-400 hover:text-white hover:border-slate-500 transition-colors font-medium"
                >
                  ← Back
                </button>
                <Button
                  onClick={handleSubmit}
                  disabled={isLoading}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold py-3 rounded-lg"
                >
                  {isLoading ? 'Setting up...' : 'Start Training! 🚀'}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
