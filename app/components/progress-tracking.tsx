'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertCircle, CheckCircle, AlertTriangle, TrendingUp, Calendar } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'

export function ProgressTracking() {
  const [daysToTrack, setDaysToTrack] = useState(7)
  const [tracking, setTracking] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleLoadTracking = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(
        `/api/v1/training/progress-tracking?days=${daysToTrack}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )
      
      if (!response.ok) throw new Error('Failed to load progress')
      const data = await response.json()
      setTracking(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Training Progress Tracker
          </CardTitle>
          <CardDescription>
            Monitor your training adaptation and identify warning signs
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Tracking Period (days)</label>
            <select
              value={daysToTrack}
              onChange={(e) => setDaysToTrack(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>Last 7 Days</option>
              <option value={14}>Last 14 Days</option>
              <option value={30}>Last 30 Days</option>
            </select>
          </div>
          <Button 
            onClick={handleLoadTracking} 
            disabled={loading}
            className="w-full"
            size="lg"
          >
            {loading ? 'Loading...' : 'Load Progress'}
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
      {tracking && (
        <div className="space-y-6">
          {/* Overview Status */}
          <Card className="border-2 border-blue-200">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Training Status</span>
                <span className="text-3xl">
                  {tracking.overall_status === 'excellent' ? '⭐' :
                   tracking.overall_status === 'good' ? '✅' :
                   tracking.overall_status === 'fair' ? '⚠️' :
                   '❌'}
                </span>
              </CardTitle>
              <CardDescription className="capitalize">
                {tracking.overall_status} • Last {daysToTrack} days
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Workouts</p>
                  <p className="text-2xl font-bold text-blue-600">{tracking.metrics.total_workouts}</p>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Adaptation</p>
                  <p className="text-2xl font-bold text-green-600">{(tracking.metrics.adaptation_rate * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Consistency</p>
                  <p className="text-2xl font-bold text-purple-600">{(tracking.metrics.consistency_score * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Injury Risk</p>
                  <p className="text-2xl font-bold text-orange-600">{tracking.metrics.injury_risk_score.toFixed(0)}/10</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Positive Signs */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                Good Adaptation Signs ({tracking.good_adaptation_signs.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {tracking.good_adaptation_signs.length > 0 ? (
                <ul className="space-y-3">
                  {tracking.good_adaptation_signs.map((sign, idx) => (
                    <li key={idx} className="flex gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                      <span className="text-lg flex-shrink-0">✅</span>
                      <span className="text-sm text-green-900">{sign}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-600">No specific positive signs detected yet. Continue tracking!</p>
              )}
            </CardContent>
          </Card>

          {/* Warning Signs */}
          {tracking.warning_signs.length > 0 && (
            <Card className="border-2 border-red-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  Warning Signs ({tracking.warning_signs.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {tracking.warning_signs.map((sign, idx) => (
                    <li key={idx} className="flex gap-3 p-3 bg-red-50 rounded-lg border border-red-200">
                      <span className="text-lg flex-shrink-0">⚠️</span>
                      <span className="text-sm text-red-900">{sign}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                AI Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {tracking.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <span className="text-lg flex-shrink-0">💡</span>
                    <span className="text-sm text-blue-900">{rec}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Detailed Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Detailed Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Adaptation Progress */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">Adaptation Progress</span>
                  <span className="text-sm font-bold">{(tracking.metrics.adaptation_rate * 100).toFixed(1)}%</span>
                </div>
                <Progress value={tracking.metrics.adaptation_rate * 100} className="h-3" />
                <p className="text-xs text-gray-600 mt-1">
                  {tracking.metrics.adaptation_rate > 0.8 ? '✅ Excellent adaptation to training load' :
                   tracking.metrics.adaptation_rate > 0.6 ? '✅ Good adaptation progress' :
                   tracking.metrics.adaptation_rate > 0.4 ? '⚠️ Moderate adaptation' :
                   '❌ Low adaptation - consider reducing load'}
                </p>
              </div>

              {/* Consistency */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">Training Consistency</span>
                  <span className="text-sm font-bold">{(tracking.metrics.consistency_score * 100).toFixed(1)}%</span>
                </div>
                <Progress value={tracking.metrics.consistency_score * 100} className="h-3" />
                <p className="text-xs text-gray-600 mt-1">
                  Workouts completed vs planned: {tracking.metrics.total_workouts} of {(tracking.metrics.total_workouts / tracking.metrics.consistency_score).toFixed(0)}
                </p>
              </div>

              {/* Recovery Score */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">Average Recovery Score</span>
                  <span className="text-sm font-bold">{tracking.metrics.avg_recovery_score.toFixed(1)}/10</span>
                </div>
                <Progress value={tracking.metrics.avg_recovery_score * 10} className="h-3" />
                <p className="text-xs text-gray-600 mt-1">
                  {tracking.metrics.avg_recovery_score > 7 ? '✅ Excellent recovery' :
                   tracking.metrics.avg_recovery_score > 5 ? '✅ Good recovery' :
                   '⚠️ May need more recovery time'}
                </p>
              </div>

              {/* Injury Risk */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">Injury Risk Score</span>
                  <span className="text-sm font-bold">{tracking.metrics.injury_risk_score.toFixed(1)}/10</span>
                </div>
                <Progress 
                  value={tracking.metrics.injury_risk_score * 10}
                  className="h-3"
                />
                <p className="text-xs text-gray-600 mt-1">
                  {tracking.metrics.injury_risk_score < 3 ? '✅ Low risk' :
                   tracking.metrics.injury_risk_score < 6 ? '⚠️ Moderate risk' :
                   '❌ High risk - monitor closely'}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Performance Trends */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Trends</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-semibold mb-2">VO2 Max Progression</p>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">
                      {tracking.vo2_max_trend > 0 ? '📈' : tracking.vo2_max_trend < 0 ? '📉' : '→'}
                    </span>
                    <span className="text-sm">
                      {tracking.vo2_max_trend > 0 ? '+' : ''}{tracking.vo2_max_trend.toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-semibold mb-2">Lactate Threshold</p>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">
                      {tracking.lactate_threshold_trend > 0 ? '📈' : tracking.lactate_threshold_trend < 0 ? '📉' : '→'}
                    </span>
                    <span className="text-sm">
                      {tracking.lactate_threshold_trend > 0 ? '+' : ''}{tracking.lactate_threshold_trend.toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-semibold mb-2">Running Economy</p>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">
                      {tracking.running_economy_trend > 0 ? '📈' : tracking.running_economy_trend < 0 ? '📉' : '→'}
                    </span>
                    <span className="text-sm">
                      {tracking.running_economy_trend > 0 ? '+' : ''}{tracking.running_economy_trend.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Next Steps */}
          <Card>
            <CardHeader>
              <CardTitle>Next Steps</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                {tracking.next_steps.map((step, idx) => (
                  <li key={idx} className="flex gap-2">
                    <span className="text-lg">→</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
