'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { RacePredictionCalculator } from './race-prediction-calculator'
import { TrainingPlanGenerator } from './training-plan-generator'
import { IntensityZonesReference } from './intensity-zones-reference'
import { AdaptiveAdjustments } from './adaptive-adjustments'
import { ProgressTracking } from './progress-tracking'
import { Trophy, Zap, Heart, Gauge, TrendingUp } from 'lucide-react'

export function TrainingDashboard() {
  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">🏃 Training Intelligence Dashboard</h1>
        <p className="text-gray-600">
          Advanced AI-powered training analysis, planning, and performance tracking
        </p>
      </div>

      {/* Quick Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Trophy className="h-4 w-4" />
              Race Prediction
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-gray-600">Predict race times with weather & terrain analysis</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Weekly Plans
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-gray-600">AI-generated adaptive training schedules</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Heart className="h-4 w-4" />
              Zone Guidance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-gray-600">Heart rate training zones & recommendations</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Gauge className="h-4 w-4" />
              Load Adjustment
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-gray-600">Real-time workout load optimization</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-red-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Progress Tracking
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-gray-600">Monitor adaptation & identify warnings</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs defaultValue="race" className="w-full">
        <TabsList className="grid w-full grid-cols-5 mb-6">
          <TabsTrigger value="race" className="flex items-center gap-2">
            <Trophy className="h-4 w-4" />
            <span className="hidden sm:inline">Race</span>
          </TabsTrigger>
          <TabsTrigger value="training" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            <span className="hidden sm:inline">Training</span>
          </TabsTrigger>
          <TabsTrigger value="zones" className="flex items-center gap-2">
            <Heart className="h-4 w-4" />
            <span className="hidden sm:inline">Zones</span>
          </TabsTrigger>
          <TabsTrigger value="load" className="flex items-center gap-2">
            <Gauge className="h-4 w-4" />
            <span className="hidden sm:inline">Load</span>
          </TabsTrigger>
          <TabsTrigger value="progress" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            <span className="hidden sm:inline">Progress</span>
          </TabsTrigger>
        </TabsList>

        {/* Race Prediction Tab */}
        <TabsContent value="race" className="space-y-4">
          <RacePredictionCalculator />
        </TabsContent>

        {/* Training Plans Tab */}
        <TabsContent value="training" className="space-y-4">
          <TrainingPlanGenerator />
        </TabsContent>

        {/* Intensity Zones Tab */}
        <TabsContent value="zones" className="space-y-4">
          <IntensityZonesReference />
        </TabsContent>

        {/* Adaptive Load Tab */}
        <TabsContent value="load" className="space-y-4">
          <AdaptiveAdjustments />
        </TabsContent>

        {/* Progress Tab */}
        <TabsContent value="progress" className="space-y-4">
          <ProgressTracking />
        </TabsContent>
      </Tabs>

      {/* Footer Info */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-sm">💡 How to Use This Dashboard</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-gray-700">
          <p>
            <strong>1. Race Prediction:</strong> Enter your recent race data and target distance to get weather-adjusted predictions
          </p>
          <p>
            <strong>2. Weekly Plans:</strong> Input your fatigue level and phase to get AI-generated training schedules
          </p>
          <p>
            <strong>3. Zone Guidance:</strong> Learn your personalized heart rate zones and training distribution
          </p>
          <p>
            <strong>4. Load Adjustment:</strong> Check real-time adjustments based on sleep, fatigue, and HRV
          </p>
          <p>
            <strong>5. Progress Tracking:</strong> Monitor your adaptation with performance trends and warning signs
          </p>
        </CardContent>
      </Card>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">🤖 AI-Powered</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-gray-600">
            All analysis powered by Groq Llama 3.3 for intelligent, personalized coaching
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">📊 Data-Driven</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-gray-600">
            Real-time metrics from your workouts, HRV, and training history
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">🎯 Actionable</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-gray-600">
            Specific recommendations you can implement immediately in your training
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
