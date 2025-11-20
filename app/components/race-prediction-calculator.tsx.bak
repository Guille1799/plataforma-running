'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertCircle, Gauge, TrendingUp, Cloud } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

export function RacePredictionCalculator() {
  const [baseDistance, setBaseDistance] = useState(10)
  const [baseTime, setBaseTime] = useState(45)
  const [targetDistance, setTargetDistance] = useState(21.1)
  const [terrain, setTerrain] = useState('rolling')
  const [temperature, setTemperature] = useState(15)
  const [humidity, setHumidity] = useState(55)
  const [wind, setWind] = useState(10)
  const [altitude, setAltitude] = useState(0)
  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState(null)
  const [error, setError] = useState(null)

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(
        `/api/v1/race/predict-with-conditions?` +
        `base_distance_km=${baseDistance}&` +
        `base_time_minutes=${baseTime}&` +
        `target_distance_km=${targetDistance}&` +
        `terrain=${terrain}&` +
        `temperature_c=${temperature}&` +
        `humidity_pct=${humidity}&` +
        `wind_kmh=${wind}&` +
        `altitude_m=${altitude}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )
      
      if (!response.ok) throw new Error('Prediction failed')
      const data = await response.json()
      setPrediction(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Race Time Predictor</CardTitle>
          <CardDescription>
            Get accurate race predictions based on your recent performance and race conditions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Base Performance */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="base-distance">Base Race Distance (km)</Label>
              <Input
                id="base-distance"
                type="number"
                value={baseDistance}
                onChange={(e) => setBaseDistance(parseFloat(e.target.value))}
                min="3"
                max="50"
                step="0.1"
                className="mt-2"
              />
            </div>
            <div>
              <Label htmlFor="base-time">Base Race Time (minutes)</Label>
              <Input
                id="base-time"
                type="number"
                value={baseTime}
                onChange={(e) => setBaseTime(parseFloat(e.target.value))}
                min="10"
                max="600"
                step="0.5"
                className="mt-2"
              />
            </div>
          </div>

          {/* Target Distance */}
          <div>
            <Label htmlFor="target-distance">Target Race Distance (km)</Label>
            <Input
              id="target-distance"
              type="number"
              value={targetDistance}
              onChange={(e) => setTargetDistance(parseFloat(e.target.value))}
              min="3"
              max="50"
              step="0.1"
              className="mt-2"
            />
          </div>

          {/* Environmental Factors */}
          <div className="border-t pt-4">
            <h3 className="font-semibold text-sm mb-4">Environmental Factors</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="terrain">Terrain Type</Label>
                <Select value={terrain} onValueChange={setTerrain}>
                  <SelectTrigger id="terrain" className="mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="flat">Flat (Road/Track)</SelectItem>
                    <SelectItem value="rolling">Rolling (Some Hills)</SelectItem>
                    <SelectItem value="hilly">Hilly (Significant Elevation)</SelectItem>
                    <SelectItem value="mountain">Mountain (Major Climbs)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="temperature">Temperature (°C)</Label>
                <Input
                  id="temperature"
                  type="number"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  min="-20"
                  max="50"
                  step="1"
                  className="mt-2"
                />
              </div>

              <div>
                <Label htmlFor="humidity">Humidity (%)</Label>
                <Input
                  id="humidity"
                  type="number"
                  value={humidity}
                  onChange={(e) => setHumidity(parseFloat(e.target.value))}
                  min="0"
                  max="100"
                  step="1"
                  className="mt-2"
                />
              </div>

              <div>
                <Label htmlFor="wind">Wind Speed (km/h)</Label>
                <Input
                  id="wind"
                  type="number"
                  value={wind}
                  onChange={(e) => setWind(parseFloat(e.target.value))}
                  min="0"
                  max="80"
                  step="1"
                  className="mt-2"
                />
              </div>

              <div>
                <Label htmlFor="altitude">Altitude (meters)</Label>
                <Input
                  id="altitude"
                  type="number"
                  value={altitude}
                  onChange={(e) => setAltitude(parseInt(e.target.value))}
                  min="0"
                  max="5000"
                  step="100"
                  className="mt-2"
                />
              </div>
            </div>
          </div>

          <Button 
            onClick={handlePredict} 
            disabled={loading}
            className="w-full"
            size="lg"
          >
            {loading ? 'Calculating...' : 'Predict Race Time'}
          </Button>
        </CardContent>
      </Card>

      {/* Results Section */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {prediction && (
        <Tabs defaultValue="prediction" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="prediction">Prediction</TabsTrigger>
            <TabsTrigger value="adjustments">Adjustments</TabsTrigger>
            <TabsTrigger value="recommendations">Tips</TabsTrigger>
          </TabsList>

          {/* Prediction Tab */}
          <TabsContent value="prediction">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Gauge className="h-5 w-5" />
                  Race Time Prediction
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Main Prediction */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg">
                  <div className="text-center">
                    <p className="text-sm font-medium text-gray-600 mb-2">Predicted Time</p>
                    <p className="text-4xl font-bold text-blue-600">
                      {prediction.prediction.formatted_time}
                    </p>
                    <p className="text-sm text-gray-600 mt-2">
                      Pace: {prediction.prediction.formatted_pace}
                    </p>
                  </div>
                </div>

                {/* Base vs Adjusted */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="border rounded-lg p-4">
                    <p className="text-xs font-semibold text-gray-500 mb-1">BASE PREDICTION</p>
                    <p className="text-lg font-bold text-gray-800">
                      {prediction.prediction.base_prediction_minutes.toFixed(1)} min
                    </p>
                  </div>
                  <div className="border border-blue-300 bg-blue-50 rounded-lg p-4">
                    <p className="text-xs font-semibold text-blue-600 mb-1">WITH CONDITIONS</p>
                    <p className="text-lg font-bold text-blue-700">
                      {prediction.prediction.adjusted_prediction_minutes.toFixed(1)} min
                    </p>
                  </div>
                </div>

                {/* Confidence Score */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">Confidence</span>
                    <span className="text-sm font-bold text-blue-600">
                      {prediction.confidence.score.toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-600 h-3 rounded-full transition-all"
                      style={{ width: `${prediction.confidence.score}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-600 mt-2">
                    Level: <span className="font-semibold capitalize">{prediction.confidence.level}</span>
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Adjustments Tab */}
          <TabsContent value="adjustments">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cloud className="h-5 w-5" />
                  Environmental Impact
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Weather Factor */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-gray-700">Weather Impact</span>
                    <span className="text-lg font-bold">
                      {((prediction.adjustments.weather_factor - 1) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-600">
                    {prediction.adjustments.weather_factor < 1 
                      ? '✅ Favorable conditions' 
                      : prediction.adjustments.weather_factor === 1
                      ? '➖ Normal conditions'
                      : '⚠️ Challenging conditions'}
                  </p>
                </div>

                {/* Terrain Factor */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-gray-700">Terrain Impact</span>
                    <span className="text-lg font-bold">
                      {((prediction.adjustments.terrain_factor - 1) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-600">
                    {prediction.conditions.terrain === 'flat' && '✅ Optimal for speed'}
                    {prediction.conditions.terrain === 'rolling' && '➖ Standard difficulty'}
                    {prediction.conditions.terrain === 'hilly' && '⚠️ Requires strength'}
                    {prediction.conditions.terrain === 'mountain' && '🏔️ Very challenging'}
                  </p>
                </div>

                {/* Altitude Factor */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-gray-700">Altitude Impact</span>
                    <span className="text-lg font-bold">
                      {((prediction.adjustments.altitude_factor - 1) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-600">
                    {prediction.conditions.altitude_m > 1500 
                      ? `⚠️ Altitude: ${prediction.conditions.altitude_m}m (reduced oxygen)`
                      : `✅ Sea level (${prediction.conditions.altitude_m}m)`}
                  </p>
                </div>

                {/* Total Adjustment */}
                <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-amber-900">Total Adjustment</span>
                    <span className="text-lg font-bold text-amber-700">
                      {(prediction.adjustments.adjustment_percentage).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Recommendations Tab */}
          <TabsContent value="recommendations">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Race Day Tips
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {prediction.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex gap-3 text-sm">
                      <span className="text-lg">{rec.substring(0, 1)}</span>
                      <span className="text-gray-700">{rec.substring(2)}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
