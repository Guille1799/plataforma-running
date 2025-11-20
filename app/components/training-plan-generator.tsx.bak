'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertCircle, Activity, Heart, Shield, TrendingUp } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'

export function TrainingPlanGenerator() {
  const [fatigueScore, setFatigueScore] = useState(50)
  const [readinessScore, setReadinessScore] = useState(50)
  const [phase, setPhase] = useState('build')
  const [maxHR, setMaxHR] = useState(190)
  const [loading, setLoading] = useState(false)
  const [plan, setPlan] = useState(null)
  const [error, setError] = useState(null)

  const handleGeneratePlan = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(
        `/api/v1/training/weekly-plan?` +
        `fatigue_score=${fatigueScore}&` +
        `readiness_score=${readinessScore}&` +
        `phase=${phase}&` +
        `max_hr=${maxHR}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )
      
      if (!response.ok) throw new Error('Plan generation failed')
      const data = await response.json()
      setPlan(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getZoneColor = (zone) => {
    switch (zone) {
      case 'z1': return 'bg-blue-100 text-blue-900'
      case 'z2': return 'bg-green-100 text-green-900'
      case 'z3': return 'bg-yellow-100 text-yellow-900'
      case 'z4': return 'bg-orange-100 text-orange-900'
      case 'z5': return 'bg-red-100 text-red-900'
      default: return 'bg-gray-100 text-gray-900'
    }
  }

  const getZoneName = (zone) => {
    const names = {
      z1: 'Recovery',
      z2: 'Aerobic',
      z3: 'Tempo',
      z4: 'Threshold',
      z5: 'Interval'
    }
    return names[zone] || zone
  }

  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Adaptive Training Plan Generator</CardTitle>
          <CardDescription>
            Get a personalized weekly training plan based on your current status
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Status Inputs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label className="flex items-center gap-2 mb-3">
                <Heart className="h-4 w-4" />
                Fatigue Score: <span className="font-bold ml-2">{fatigueScore}</span>
              </Label>
              <input
                type="range"
                min="0"
                max="100"
                value={fatigueScore}
                onChange={(e) => setFatigueScore(parseInt(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-gray-600 mt-1">
                {fatigueScore < 33 ? '✅ Fresh' : fatigueScore < 67 ? '⚠️ Moderate' : '🔴 High'}
              </p>
            </div>

            <div>
              <Label className="flex items-center gap-2 mb-3">
                <TrendingUp className="h-4 w-4" />
                Readiness Score: <span className="font-bold ml-2">{readinessScore}</span>
              </Label>
              <input
                type="range"
                min="0"
                max="100"
                value={readinessScore}
                onChange={(e) => setReadinessScore(parseInt(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-gray-600 mt-1">
                {readinessScore > 70 ? '✅ Peak Ready' : readinessScore > 40 ? '➖ Normal' : '🔴 Low'}
              </p>
            </div>
          </div>

          {/* Training Phase */}
          <div>
            <Label htmlFor="phase">Training Phase</Label>
            <Select value={phase} onValueChange={setPhase}>
              <SelectTrigger id="phase" className="mt-2">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="base">Base Phase (Build aerobic foundation)</SelectItem>
                <SelectItem value="build">Build Phase (Intensity building)</SelectItem>
                <SelectItem value="peak">Peak Phase (Race-specific prep)</SelectItem>
                <SelectItem value="taper">Taper Phase (Pre-race recovery)</SelectItem>
                <SelectItem value="recovery">Recovery Phase (Active recovery)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Max HR */}
          <div>
            <Label htmlFor="max-hr">Maximum Heart Rate (BPM)</Label>
            <Input
              id="max-hr"
              type="number"
              value={maxHR}
              onChange={(e) => setMaxHR(parseInt(e.target.value))}
              min="100"
              max="250"
              className="mt-2"
            />
          </div>

          <Button 
            onClick={handleGeneratePlan} 
            disabled={loading}
            className="w-full"
            size="lg"
          >
            {loading ? 'Generating Plan...' : 'Generate Weekly Plan'}
          </Button>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Results */}
      {plan && (
        <Tabs defaultValue="weekly" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="weekly">Weekly Plan</TabsTrigger>
            <TabsTrigger value="zones">Zones</TabsTrigger>
            <TabsTrigger value="tips">Tips</TabsTrigger>
            <TabsTrigger value="injury">Prevention</TabsTrigger>
          </TabsList>

          {/* Weekly Plan Tab */}
          <TabsContent value="weekly">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  7-Day Training Schedule
                </CardTitle>
                <CardDescription>
                  {plan.week_plan.phase.charAt(0).toUpperCase() + plan.week_plan.phase.slice(1)} Phase • 
                  {plan.week_plan.total_load_minutes} min/week • 
                  Load: {(plan.week_plan.load_adjustment_factor * 100).toFixed(0)}%
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {plan.week_plan.daily_workouts.map((workout, idx) => (
                  <div key={idx} className="border rounded-lg p-4 hover:bg-gray-50 transition">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="font-bold text-lg">{dayNames[idx]}</p>
                        <p className="text-xs text-gray-600 capitalize">{workout.type}</p>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getZoneColor(workout.primary_zone)}`}>
                        {getZoneName(workout.primary_zone)}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <p className="text-sm text-gray-700">{workout.description}</p>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">
                          Duration: <span className="font-semibold">{workout.duration_minutes} min</span>
                        </span>
                        <span className="text-gray-600">
                          HR Range: <span className="font-semibold">{workout.zone_range_bpm.min}-{workout.zone_range_bpm.max} BPM</span>
                        </span>
                      </div>

                      {workout.adaptive_notes !== 'Standard workout' && (
                        <p className="text-xs bg-amber-50 text-amber-900 p-2 rounded italic">
                          {workout.adaptive_notes}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Intensity Zones Tab */}
          <TabsContent value="zones">
            <Card>
              <CardHeader>
                <CardTitle>Weekly Intensity Distribution</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {Object.entries(plan.weekly_metrics.intensity_distribution).map(([zone, percentage]) => (
                  <div key={zone}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold capitalize">{getZoneName(zone)}</span>
                      <span className="text-sm font-bold">{percentage.toFixed(1)}%</span>
                    </div>
                    <Progress value={percentage} className="h-3" />
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tips Tab */}
          <TabsContent value="tips">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  AI Coaching Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {plan.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex gap-3 text-sm">
                      <span className="text-lg">{rec.charAt(0)}</span>
                      <span className="text-gray-700">{rec.slice(2)}</span>
                    </li>
                  ))}
                </ul>

                <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm font-semibold text-blue-900 mb-2">Status: {plan.athlete_status.status}</p>
                  <p className="text-xs text-blue-800">
                    Fatigue: {plan.athlete_status.fatigue_score.toFixed(0)}/100 • 
                    Readiness: {plan.athlete_status.readiness_score.toFixed(0)}/100
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Injury Prevention Tab */}
          <TabsContent value="injury">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Injury Prevention Strategy
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Strength Training */}
                <div>
                  <h3 className="font-semibold mb-3">Strength Training</h3>
                  <ul className="space-y-2">
                    {plan.injury_prevention.strength_training.map((ex, idx) => (
                      <li key={idx} className="text-sm flex gap-2">
                        <span>💪</span>
                        <span>{ex}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Stretching */}
                <div>
                  <h3 className="font-semibold mb-3">Stretching Routine</h3>
                  <ul className="space-y-2">
                    {plan.injury_prevention.stretching.map((stretch, idx) => (
                      <li key={idx} className="text-sm flex gap-2">
                        <span>🧘</span>
                        <span>{stretch}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Warnings */}
                {plan.injury_prevention.warnings.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h3 className="font-semibold text-red-900 mb-2">⚠️ Warnings</h3>
                    <ul className="space-y-1">
                      {plan.injury_prevention.warnings.map((warning, idx) => (
                        <li key={idx} className="text-xs text-red-800">{warning}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
