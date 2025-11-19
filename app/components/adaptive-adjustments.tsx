'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertCircle, Activity, Gauge, Lightbulb, TrendingDown } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'

export function AdaptiveAdjustments() {
  const [fatigueLevel, setFatigueLevel] = useState(50)
  const [previousHRV, setPreviousHRV] = useState(55)
  const [hrVariability, setHRVariability] = useState(5)
  const [sleepHours, setSleepHours] = useState(7)
  const [adjustment, setAdjustment] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleCalculateAdjustment = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(
        `/api/v1/training/adaptive-adjustment?` +
        `fatigue_level=${fatigueLevel}&` +
        `previous_hrv=${previousHRV}&` +
        `current_hr_variability=${hrVariability}&` +
        `sleep_hours=${sleepHours}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )
      
      if (!response.ok) throw new Error('Adjustment calculation failed')
      const data = await response.json()
      setAdjustment(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getAdjustmentColor = (value) => {
    if (value > 1.1) return { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-900', indicator: '🔴' }
    if (value > 1.0) return { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-900', indicator: '🟠' }
    if (value > 0.9) return { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-900', indicator: '🟢' }
    return { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-900', indicator: '🔵' }
  }

  const getLoadStatus = (factor) => {
    if (factor > 1.15) return { status: 'Increase Needed', icon: '⬆️', color: 'text-red-600' }
    if (factor > 1.05) return { status: 'Light Increase', icon: '↗️', color: 'text-orange-600' }
    if (factor >= 0.95) return { status: 'Optimal', icon: '➡️', color: 'text-green-600' }
    if (factor > 0.85) return { status: 'Light Reduce', icon: '↘️', color: 'text-orange-600' }
    return { status: 'Reduce Load', icon: '⬇️', color: 'text-blue-600' }
  }

  return (
    <div className="space-y-6">
      {/* Input Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Gauge className="h-5 w-5" />
            Real-Time Load Adjustment
          </CardTitle>
          <CardDescription>
            Get personalized training load adjustments based on your current status
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Fatigue Level */}
          <div>
            <Label className="flex items-center gap-2 mb-3">
              <Activity className="h-4 w-4" />
              Fatigue Level: <span className="font-bold ml-2">{fatigueLevel}</span>/100
            </Label>
            <input
              type="range"
              min="0"
              max="100"
              value={fatigueLevel}
              onChange={(e) => setFatigueLevel(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-600 mt-1">
              <span>Fresh</span>
              <span>Moderate</span>
              <span>Exhausted</span>
            </div>
          </div>

          {/* Previous HRV */}
          <div>
            <label className="block text-sm font-medium mb-2">Previous HRV Score</label>
            <input
              type="number"
              value={previousHRV}
              onChange={(e) => setPreviousHRV(parseInt(e.target.value))}
              min="0"
              max="100"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
            <p className="text-xs text-gray-600 mt-1">Last recorded HRV (0-100)</p>
          </div>

          {/* HR Variability Change */}
          <div>
            <label className="block text-sm font-medium mb-2">HR Variability Change (BPM)</label>
            <input
              type="number"
              value={hrVariability}
              onChange={(e) => setHRVariability(parseFloat(e.target.value))}
              min="-10"
              max="10"
              step="0.5"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
            <p className="text-xs text-gray-600 mt-1">Change from baseline (negative = better)</p>
          </div>

          {/* Sleep */}
          <div>
            <label className="block text-sm font-medium mb-2">Sleep Last Night (hours)</label>
            <input
              type="number"
              value={sleepHours}
              onChange={(e) => setSleepHours(parseFloat(e.target.value))}
              min="0"
              max="12"
              step="0.5"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
            <p className="text-xs text-gray-600 mt-1">7-9 hours is optimal</p>
          </div>

          <Button 
            onClick={handleCalculateAdjustment} 
            disabled={loading}
            className="w-full"
            size="lg"
          >
            {loading ? 'Calculating...' : 'Get Load Adjustment'}
          </Button>
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Results */}
      {adjustment && (
        <Tabs defaultValue="adjustment" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="adjustment">Load Adjustment</TabsTrigger>
            <TabsTrigger value="workout">Workout Modification</TabsTrigger>
            <TabsTrigger value="recovery">Recovery Tips</TabsTrigger>
          </TabsList>

          {/* Load Adjustment Tab */}
          <TabsContent value="adjustment">
            <div className="space-y-4">
              {/* Main Factor */}
              <Card className="border-2 border-blue-200">
                <CardHeader>
                  <CardTitle className="text-2xl">
                    Load Adjustment Factor
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="text-center">
                      <div className="text-5xl font-bold text-blue-600 mb-2">
                        {adjustment.adjustment_factor.toFixed(2)}x
                      </div>
                      <p className="text-gray-600 mb-4">
                        {getLoadStatus(adjustment.adjustment_factor).status}
                      </p>
                    </div>

                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm font-semibold mb-2">How to Use:</p>
                      <p className="text-sm text-gray-700">
                        Multiply your planned workout volume by <span className="font-bold text-blue-600">{adjustment.adjustment_factor.toFixed(2)}</span>
                      </p>
                      <p className="text-xs text-gray-600 mt-2">
                        Example: 60 min planned = {(60 * adjustment.adjustment_factor).toFixed(0)} min adjusted
                      </p>
                    </div>

                    {/* Components */}
                    <div className="grid grid-cols-2 gap-3 pt-4 border-t">
                      <div className="bg-green-50 p-3 rounded">
                        <p className="text-xs font-semibold text-green-900">Readiness Factor</p>
                        <p className="text-2xl font-bold text-green-600">{adjustment.readiness_factor.toFixed(2)}x</p>
                      </div>
                      <div className="bg-orange-50 p-3 rounded">
                        <p className="text-xs font-semibold text-orange-900">Fatigue Factor</p>
                        <p className="text-2xl font-bold text-orange-600">{adjustment.fatigue_factor.toFixed(2)}x</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Detailed Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5" />
                    Adjustment Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="font-semibold mb-2">Readiness Indicators</p>
                    <ul className="space-y-2">
                      <li className="text-sm flex gap-2">
                        <span>{sleepHours >= 7 ? '✅' : '⚠️'}</span>
                        <span>Sleep: {sleepHours}h ({sleepHours >= 7 ? 'Optimal' : sleepHours >= 6 ? 'Adequate' : 'Insufficient'})</span>
                      </li>
                      <li className="text-sm flex gap-2">
                        <span>{previousHRV > 50 ? '✅' : '⚠️'}</span>
                        <span>HRV Trend: {previousHRV} ({previousHRV > 60 ? 'Strong' : previousHRV > 50 ? 'Normal' : 'Low'})</span>
                      </li>
                      <li className="text-sm flex gap-2">
                        <span>{fatigueLevel < 60 ? '✅' : fatigueLevel < 75 ? '⚠️' : '❌'}</span>
                        <span>Fatigue: {fatigueLevel} ({fatigueLevel < 60 ? 'Low' : fatigueLevel < 75 ? 'Moderate' : 'High'})</span>
                      </li>
                      <li className="text-sm flex gap-2">
                        <span>{hrVariability < 3 ? '✅' : '⚠️'}</span>
                        <span>HR Variability: {hrVariability > 0 ? '+' : ''}{hrVariability} BPM</span>
                      </li>
                    </ul>
                  </div>

                  <div className="border-t pt-4">
                    <p className="font-semibold mb-2">Status Summary</p>
                    <p className="text-sm text-gray-700">{adjustment.recommendation}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Workout Modification Tab */}
          <TabsContent value="workout">
            <Card>
              <CardHeader>
                <CardTitle>How to Modify Your Workout</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Duration */}
                <div>
                  <p className="font-semibold mb-3">Duration Adjustment</p>
                  <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                    <p className="text-sm mb-2">
                      <span className="font-semibold">Original:</span> 60 minutes
                    </p>
                    <p className="text-sm mb-3">
                      <span className="font-semibold">Adjusted:</span> {(60 * adjustment.adjustment_factor).toFixed(0)} minutes
                    </p>
                    <p className="text-xs text-gray-600">
                      × {adjustment.adjustment_factor.toFixed(2)} adjustment factor
                    </p>
                  </div>
                </div>

                {/* Intensity */}
                <div>
                  <p className="font-semibold mb-3">Intensity Adjustment</p>
                  <div className={`p-4 rounded-lg border-2 ${
                    adjustment.adjustment_factor > 1 ? 'bg-red-50 border-red-200' : 
                    adjustment.adjustment_factor < 0.9 ? 'bg-blue-50 border-blue-200' : 
                    'bg-green-50 border-green-200'
                  }`}>
                    {adjustment.adjustment_factor > 1.1 && (
                      <p className="text-sm text-red-900">
                        🔴 <span className="font-semibold">INCREASE</span> intensity: Consider adding harder efforts
                      </p>
                    )}
                    {adjustment.adjustment_factor > 1 && adjustment.adjustment_factor <= 1.1 && (
                      <p className="text-sm text-orange-900">
                        🟠 <span className="font-semibold">SLIGHTLY INCREASE:</span> Add 1-2 threshold efforts if planned
                      </p>
                    )}
                    {adjustment.adjustment_factor >= 0.95 && adjustment.adjustment_factor <= 1 && (
                      <p className="text-sm text-green-900">
                        🟢 <span className="font-semibold">MAINTAIN:</span> Keep planned intensity as scheduled
                      </p>
                    )}
                    {adjustment.adjustment_factor < 0.95 && adjustment.adjustment_factor > 0.85 && (
                      <p className="text-sm text-orange-900">
                        🟠 <span className="font-semibold">SLIGHTLY REDUCE:</span> Skip hard repeats, keep easy pace
                      </p>
                    )}
                    {adjustment.adjustment_factor <= 0.85 && (
                      <p className="text-sm text-blue-900">
                        🔵 <span className="font-semibold">REDUCE:</span> Easy recovery run or light workout only
                      </p>
                    )}
                  </div>
                </div>

                {/* Volume */}
                <div>
                  <p className="font-semibold mb-3">Volume Examples</p>
                  <div className="space-y-2 text-sm">
                    <p>📊 <span className="font-semibold">30 min planned:</span> {(30 * adjustment.adjustment_factor).toFixed(0)} min adjusted</p>
                    <p>📊 <span className="font-semibold">45 min planned:</span> {(45 * adjustment.adjustment_factor).toFixed(0)} min adjusted</p>
                    <p>📊 <span className="font-semibold">60 min planned:</span> {(60 * adjustment.adjustment_factor).toFixed(0)} min adjusted</p>
                    <p>📊 <span className="font-semibold">90 min planned:</span> {(90 * adjustment.adjustment_factor).toFixed(0)} min adjusted</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Recovery Tab */}
          <TabsContent value="recovery">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingDown className="h-5 w-5" />
                  Recovery Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Priority Recovery Actions */}
                <div>
                  <p className="font-semibold mb-3">Priority Recovery Actions</p>
                  <ul className="space-y-2">
                    {sleepHours < 7 && (
                      <li className="flex gap-2 text-sm p-2 bg-red-50 rounded">
                        <span>🚨</span>
                        <span>Sleep is below optimal: Aim for 8-9 hours tonight</span>
                      </li>
                    )}
                    {fatigueLevel > 70 && (
                      <li className="flex gap-2 text-sm p-2 bg-orange-50 rounded">
                        <span>⚠️</span>
                        <span>High fatigue detected: Consider massage or foam rolling</span>
                      </li>
                    )}
                    {hrVariability > 3 && (
                      <li className="flex gap-2 text-sm p-2 bg-yellow-50 rounded">
                        <span>💡</span>
                        <span>HR variability elevated: Focus on breathing exercises (5-10 min)</span>
                      </li>
                    )}
                    {previousHRV < 40 && (
                      <li className="flex gap-2 text-sm p-2 bg-red-50 rounded">
                        <span>🚨</span>
                        <span>HRV is low: Consider extra rest day or easy recovery run</span>
                      </li>
                    )}
                    {adjustment.adjustment_factor < 0.9 && (
                      <li className="flex gap-2 text-sm p-2 bg-blue-50 rounded">
                        <span>💧</span>
                        <span>Load factor low: Prioritize hydration and nutrition</span>
                      </li>
                    )}
                  </ul>
                </div>

                {/* Recovery Protocol */}
                <div className="border-t pt-4">
                  <p className="font-semibold mb-3">Recommended Recovery Protocol</p>
                  <div className="space-y-3">
                    <div className="flex gap-3">
                      <span className="text-2xl">🧊</span>
                      <div>
                        <p className="font-medium text-sm">Ice Bath (optional)</p>
                        <p className="text-xs text-gray-600">10-15 min if high fatigue (>70)</p>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <span className="text-2xl">🧘</span>
                      <div>
                        <p className="font-medium text-sm">Stretching Routine</p>
                        <p className="text-xs text-gray-600">10-15 min focusing on legs/hips</p>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <span className="text-2xl">🥗</span>
                      <div>
                        <p className="font-medium text-sm">Nutrition</p>
                        <p className="text-xs text-gray-600">Carbs + protein within 30 min post-workout</p>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <span className="text-2xl">💧</span>
                      <div>
                        <p className="font-medium text-sm">Hydration</p>
                        <p className="text-xs text-gray-600">{Math.ceil((60 * adjustment.adjustment_factor) / 4)} oz fluid per 30 min activity</p>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <span className="text-2xl">😴</span>
                      <div>
                        <p className="font-medium text-sm">Sleep Target</p>
                        <p className="text-xs text-gray-600">{sleepHours < 7 ? '8-9 hours tonight' : '7-8 hours recommended'}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}

function Label({ children, className }) {
  return <label className={`block font-medium ${className}`}>{children}</label>
}
