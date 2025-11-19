'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertCircle, Heart, Info, Zap } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

export function IntensityZonesReference() {
  const [maxHR, setMaxHR] = useState(190)
  const [zones, setZones] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleLoadZones = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(
        `/api/v1/training/intensity-zones?max_hr=${maxHR}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )
      
      if (!response.ok) throw new Error('Failed to load zones')
      const data = await response.json()
      setZones(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const zoneColors = {
    z1: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-900', bar: 'bg-blue-500' },
    z2: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-900', bar: 'bg-green-500' },
    z3: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-900', bar: 'bg-yellow-500' },
    z4: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-900', bar: 'bg-orange-500' },
    z5: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-900', bar: 'bg-red-500' }
  }

  const zoneInfo = {
    z1: {
      name: 'Zone 1: Recovery',
      effort: 'Very Light',
      breathing: 'Can sing',
      description: 'Easy warm-up pace. Promotes active recovery and aerobic base building.',
      benefits: ['Builds aerobic foundation', 'Promotes recovery', 'Low injury risk'],
      workouts: ['Easy runs', 'Warm-ups', 'Cool-downs', 'Recovery days']
    },
    z2: {
      name: 'Zone 2: Aerobic',
      effort: 'Light',
      breathing: 'Can talk',
      description: 'Conversational pace. Builds strong aerobic base and fat-burning efficiency.',
      benefits: ['Improves endurance', 'Fat adaptation', 'Long-term performance'],
      workouts: ['Long runs', 'Easy runs', 'Base-building workouts']
    },
    z3: {
      name: 'Zone 3: Tempo',
      effort: 'Moderate',
      breathing: 'Can speak short sentences',
      description: 'Comfortably hard pace. Improves lactate threshold and running economy.',
      benefits: ['Increases lactate threshold', 'Improves running economy', 'Mental toughness'],
      workouts: ['Tempo runs', 'Fartlek', 'Steady-state runs']
    },
    z4: {
      name: 'Zone 4: Threshold',
      effort: 'Hard',
      breathing: 'Can barely speak',
      description: 'Very hard pace. Trains maximal aerobic power and race-pace fitness.',
      benefits: ['Increases VO2 max', 'Race-pace training', 'Peak performance'],
      workouts: ['Interval training', 'Threshold repeats', 'Race-pace runs']
    },
    z5: {
      name: 'Zone 5: Interval',
      effort: 'Maximum',
      breathing: 'Cannot speak',
      description: 'Maximum effort. Develops speed, power, and anaerobic capacity.',
      benefits: ['Builds speed', 'Anaerobic training', 'Peak competition fitness'],
      workouts: ['Sprints', 'Short intervals', 'High-intensity repeats']
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5" />
            Heart Rate Zone Calculator
          </CardTitle>
          <CardDescription>
            Calculate your personalized training zones based on maximum heart rate
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Maximum Heart Rate (BPM)</label>
            <input
              type="number"
              value={maxHR}
              onChange={(e) => setMaxHR(parseInt(e.target.value))}
              min="100"
              max="250"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-600 mt-1">
              💡 220 - age = estimated max HR (e.g., 220 - 30 = 190)
            </p>
          </div>
          <Button 
            onClick={handleLoadZones} 
            disabled={loading}
            className="w-full"
          >
            {loading ? 'Calculating Zones...' : 'Calculate My Zones'}
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

      {/* Zone Display */}
      {zones && (
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="detailed">Detailed Info</TabsTrigger>
            <TabsTrigger value="training">Training Guide</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="space-y-4">
              {Object.entries(zones.zones).map(([zoneKey, zoneData]) => {
                const colors = zoneColors[zoneKey]
                const percentage = ((zoneData.max - zoneData.min) / maxHR) * 100
                
                return (
                  <Card key={zoneKey} className={`border-2 ${colors.border}`}>
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <h3 className="font-bold text-lg">{zoneInfo[zoneKey].name}</h3>
                          <span className={`text-sm font-semibold px-3 py-1 rounded-full ${colors.bg} ${colors.text}`}>
                            {zoneInfo[zoneKey].effort}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-2xl font-bold">{zoneData.min} - {zoneData.max} BPM</span>
                          <span className="text-xs text-gray-600">{percentage.toFixed(1)}% of Max HR</span>
                        </div>

                        {/* HR Bar */}
                        <div className="h-8 bg-gray-200 rounded-full overflow-hidden flex">
                          <div 
                            className={`${colors.bar} transition-all duration-300`}
                            style={{ width: `${percentage}%` }}
                          />
                        </div>

                        <p className="text-sm text-gray-700">{zoneData.description}</p>
                        <p className="text-xs text-gray-600 italic">💬 {zoneInfo[zoneKey].breathing}</p>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>

          {/* Detailed Tab */}
          <TabsContent value="detailed">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(zones.zones).map(([zoneKey, zoneData]) => {
                const colors = zoneColors[zoneKey]
                const info = zoneInfo[zoneKey]
                
                return (
                  <Card key={zoneKey} className={`${colors.bg} border-2 ${colors.border}`}>
                    <CardHeader>
                      <CardTitle className={`text-lg ${colors.text}`}>{info.name}</CardTitle>
                      <CardDescription>{zoneData.min} - {zoneData.max} BPM</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <p className="text-xs font-semibold mb-2">💪 Benefits:</p>
                        <ul className="space-y-1">
                          {info.benefits.map((benefit, idx) => (
                            <li key={idx} className="text-xs">✓ {benefit}</li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <p className="text-xs font-semibold mb-2">🏃 RPE Descriptors:</p>
                        <p className="text-xs">• Effort: {info.effort}</p>
                        <p className="text-xs">• Breathing: {info.breathing}</p>
                      </div>

                      <div className="pt-2 border-t">
                        <p className="text-xs text-gray-700 leading-relaxed">{info.description}</p>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>

          {/* Training Guide Tab */}
          <TabsContent value="training">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Weekly Training Distribution
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Optimal weekly mix: 80% Zone 1-2, 15% Zone 3, 5% Zone 4-5
                  </AlertDescription>
                </Alert>

                {Object.entries(zones.zones).map(([zoneKey, zoneData]) => {
                  const colors = zoneColors[zoneKey]
                  const info = zoneInfo[zoneKey]
                  
                  return (
                    <div key={zoneKey}>
                      <h3 className={`font-semibold mb-2 ${colors.text}`}>{info.name}</h3>
                      <div className="mb-3">
                        <p className="text-xs font-medium mb-1">Recommended Workouts:</p>
                        <ul className="space-y-1">
                          {info.workouts.map((workout, idx) => (
                            <li key={idx} className="text-xs text-gray-700">
                              • {workout}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div className="mb-3">
                        <p className="text-xs font-medium mb-1">Duration Guidelines:</p>
                        <p className="text-xs text-gray-700">
                          {zoneKey === 'z1' && '30-90 minutes per session'}
                          {zoneKey === 'z2' && '60-180 minutes per session'}
                          {zoneKey === 'z3' && '20-40 minutes per session'}
                          {zoneKey === 'z4' && '4-8 x 3-8 minutes with recovery'}
                          {zoneKey === 'z5' && '6-12 x 30-90 seconds with recovery'}
                        </p>
                      </div>
                      <div className={`p-2 rounded ${colors.bg} border ${colors.border}`}>
                        <p className="text-xs font-medium">Weekly Frequency:</p>
                        <p className="text-xs">
                          {zoneKey === 'z1' && '3-4 times per week'}
                          {zoneKey === 'z2' && '2-4 times per week'}
                          {zoneKey === 'z3' && '1-2 times per week'}
                          {zoneKey === 'z4' && '1 time per week'}
                          {zoneKey === 'z5' && '1 time per week (sparingly)'}
                        </p>
                      </div>
                    </div>
                  )
                })}

                <div className="border-t pt-4 mt-4">
                  <h3 className="font-semibold mb-3">📊 Weekly Training Sample</h3>
                  <div className="space-y-2 text-xs">
                    <p>📅 <span className="font-medium">Monday:</span> Rest or Z1 (20 min easy)</p>
                    <p>📅 <span className="font-medium">Tuesday:</span> Z2 (45 min aerobic run)</p>
                    <p>📅 <span className="font-medium">Wednesday:</span> Z3 + Z4 (8x 3 min threshold repeats)</p>
                    <p>📅 <span className="font-medium">Thursday:</span> Z1 (30 min recovery)</p>
                    <p>📅 <span className="font-medium">Friday:</span> Rest</p>
                    <p>📅 <span className="font-medium">Saturday:</span> Z2 (60-90 min long run)</p>
                    <p>📅 <span className="font-medium">Sunday:</span> Z1 (30 min easy) or Rest</p>
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
