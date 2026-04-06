'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { manualSync, getLastSyncTime, formatTimeSinceSync } from '@/hooks/useAutoSync';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function GarminPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'garmin' | 'strava'>('garmin');

  // Garmin state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<string>('');

  // Strava state
  const [isConnectingStrava, setIsConnectingStrava] = useState(false);
  const [stravaConnected, setStravaConnected] = useState(false);

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Update last sync time on mount and periodically
  useEffect(() => {
    const updateSyncTime = () => {
      setLastSyncTime(formatTimeSinceSync());
    };

    updateSyncTime();
    const interval = setInterval(updateSyncTime, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsConnecting(true);

    try {
      await apiClient.connectGarmin({ email, password });
      setSuccess('Connected successfully! You can now sync your workouts.');
      setEmail('');
      setPassword('');
    } catch (err: any) {
      console.error('Error connecting Garmin:', err);
      const status = err.response?.status;
      const detail = err.response?.data?.detail;
      if (status === 429) {
        setError('Garmin is rate-limiting. Wait a few minutes and try again.');
      } else if (status === 401) {
        setError('Wrong email or password for Garmin Connect.');
      } else {
        setError(detail || 'Failed to connect Garmin. Check your credentials.');
      }
    } finally {
      setIsConnecting(false);
    }
  };

  const handleSync = async () => {
    setError('');
    setSuccess('');
    setIsSyncing(true);

    try {
      const result = await manualSync();

      if (result.success) {
        setSuccess(result.message);
        setLastSyncTime(formatTimeSinceSync());

        // Redirigir a workouts después de 2 segundos si hay nuevos datos
        if (result.count > 0) {
          setTimeout(() => {
            router.push('/workouts');
          }, 2000);
        }
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      console.error('Error syncing Garmin:', err);
      setError('Sync failed. Make sure your Garmin account is connected.');
    } finally {
      setIsSyncing(false);
    }
  };

  const handleConnectStrava = async () => {
    setError('');
    setSuccess('');
    setIsConnectingStrava(true);

    try {
      // Call backend to get OAuth URL
      const response = await apiClient.initStravaAuth?.();
      if (response?.authorization_url) {
        // Redirect to Strava OAuth
        window.location.href = response.authorization_url;
      }
    } catch (err: any) {
      console.error('Error connecting Strava:', err);
      setError(err.response?.data?.detail || 'Error al conectar con Strava');
      setIsConnectingStrava(false);
    }
  };

  const handleDisconnectStrava = async () => {
    setError('');
    setSuccess('');

    try {
      await apiClient.disconnectStrava?.();
      setSuccess('Strava desconectado exitosamente');
      setStravaConnected(false);
    } catch (err: any) {
      console.error('Error disconnecting Strava:', err);
      setError(err.response?.data?.detail || 'Error al desconectar Strava');
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Integrations 🔗
          </h1>
          <p className="text-slate-400">
            Connect your devices and favourite services
          </p>
        </div>

        {/* Tabs */}
        <div className="flex space-x-2 border-b border-slate-700">
          <button
            onClick={() => setActiveTab('garmin')}
            className={`px-6 py-3 font-medium transition-colors ${activeTab === 'garmin'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-slate-400 hover:text-slate-200'
              }`}
          >
            ⌚ Garmin
          </button>
          <button
            onClick={() => setActiveTab('strava')}
            className={`px-6 py-3 font-medium transition-colors ${activeTab === 'strava'
                ? 'text-orange-400 border-b-2 border-orange-400'
                : 'text-slate-400 hover:text-slate-200'
              }`}
          >
            🚴 Strava
          </button>
        </div>

        {/* Status Messages */}
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

        {/* Garmin Tab */}
        {activeTab === 'garmin' && (
          <>
            {/* Info Card */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">How it works</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-slate-300">
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">1️⃣</span>
                  <div>
                    <p className="font-semibold">Connect your account</p>
                    <p className="text-sm text-slate-400">
                      Enter your Garmin Connect credentials to authorise access
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">2️⃣</span>
                  <div>
                    <p className="font-semibold">Sync workouts</p>
                    <p className="text-sm text-slate-400">
                      Automatically import all your recent training sessions
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">3️⃣</span>
                  <div>
                    <p className="font-semibold">Analyse with AI</p>
                    <p className="text-sm text-slate-400">
                      Get personalised insights and adaptive training plans
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Connect Form */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Connect Garmin Account</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleConnect} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-slate-200">
                      Garmin email
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@email.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="bg-slate-900/50 border-slate-700 text-white"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-slate-200">
                      Garmin password
                    </Label>
                    <Input
                      id="password"
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="bg-slate-900/50 border-slate-700 text-white"
                    />
                  </div>

                  <div className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-3">
                    <p className="text-sm text-blue-200">
                      🔒 Your credentials are secure. We use garth for safe OAuth authentication.
                    </p>
                  </div>

                  <Button
                    type="submit"
                    disabled={isConnecting}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    {isConnecting ? 'Connecting...' : '🔗 Connect Garmin'}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Sync Card */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                  <span>Sync Workouts</span>
                  {lastSyncTime && (
                    <span className="text-sm font-normal text-slate-400">
                      Last sync: {lastSyncTime}
                    </span>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <p className="text-slate-300">
                    Once connected, sync your workouts from Garmin Connect.
                  </p>
                  <div className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-3 text-sm text-blue-200">
                    <p className="font-semibold mb-1">🔄 Auto-sync active</p>
                    <p className="text-xs">
                      Workouts sync automatically every 6 hours when you open the app.
                      You can also sync manually any time.
                    </p>
                  </div>
                  <div className="bg-slate-700/30 border border-slate-600 rounded-lg p-3 text-sm text-slate-300">
                    <p><strong>First sync:</strong> Imports up to 2 years of workouts and health metrics</p>
                    <p><strong>Subsequent syncs:</strong> Only new data since the last sync</p>
                  </div>
                </div>

                <Button
                  onClick={handleSync}
                  disabled={isSyncing}
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  {isSyncing ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Syncing...
                    </span>
                  ) : (
                    '🔄 Sync Now'
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Help */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-6">
                <p className="text-sm text-slate-400">
                  <strong className="text-slate-300">💡 Note:</strong> If you have trouble syncing,
                  make sure your Garmin credentials are correct and your account is active.
                  The first sync may take up to a minute.
                </p>
              </CardContent>
            </Card>
          </>
        )}

        {/* Strava Tab */}
        {activeTab === 'strava' && (
          <>
            {/* Info Card */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <span className="text-3xl">🚴</span>
                  Conectar con Strava
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-slate-300">
                  Strava es la red social para atletas. Conecta tu cuenta para sincronizar
                  tus entrenamientos automáticamente.
                </p>

                <div className="space-y-3 text-slate-300">
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">✅</span>
                    <div>
                      <p className="font-semibold">Sincronización automática</p>
                      <p className="text-sm text-slate-400">
                        Tus entrenamientos se importan automáticamente desde Strava
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">📊</span>
                    <div>
                      <p className="font-semibold">Análisis detallado</p>
                      <p className="text-sm text-slate-400">
                        Distancia, pace, frecuencia cardíaca, elevación y más
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">🔒</span>
                    <div>
                      <p className="font-semibold">OAuth 2.0 seguro</p>
                      <p className="text-sm text-slate-400">
                        No guardamos tus credenciales, solo tokens de acceso
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Connect/Disconnect Card */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Estado de Conexión</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {stravaConnected ? (
                  <>
                    <div className="flex items-center space-x-3 p-4 bg-green-900/30 border border-green-700/50 rounded-lg">
                      <span className="text-3xl">✅</span>
                      <div>
                        <p className="font-semibold text-green-300">Conectado a Strava</p>
                        <p className="text-sm text-green-400">
                          Tus entrenamientos se sincronizan automáticamente
                        </p>
                      </div>
                    </div>

                    <Button
                      onClick={handleDisconnectStrava}
                      variant="outline"
                      className="w-full border-red-700 text-red-400 hover:bg-red-900/30"
                    >
                      Desconectar Strava
                    </Button>
                  </>
                ) : (
                  <>
                    <p className="text-slate-300">
                      Haz clic en el botón para autorizar el acceso a tu cuenta de Strava.
                      Serás redirigido a Strava para aprobar la conexión.
                    </p>

                    <div className="bg-orange-900/30 border border-orange-700/50 rounded-lg p-3">
                      <p className="text-sm text-orange-200">
                        💡 Necesitarás una cuenta de Strava activa para continuar
                      </p>
                    </div>

                    <Button
                      onClick={handleConnectStrava}
                      disabled={isConnectingStrava}
                      className="w-full bg-orange-600 hover:bg-orange-700"
                    >
                      {isConnectingStrava ? 'Conectando...' : '🚴 Conectar con Strava'}
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Features Card */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">¿Qué datos se sincronizan?</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2 text-slate-300">
                      <span>✓</span>
                      <span>Distancia y duración</span>
                    </div>
                    <div className="flex items-center space-x-2 text-slate-300">
                      <span>✓</span>
                      <span>Pace y velocidad</span>
                    </div>
                    <div className="flex items-center space-x-2 text-slate-300">
                      <span>✓</span>
                      <span>Frecuencia cardíaca</span>
                    </div>
                    <div className="flex items-center space-x-2 text-slate-300">
                      <span>✓</span>
                      <span>Cadencia</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2 text-slate-300">
                      <span>✓</span>
                      <span>Elevación</span>
                    </div>
                    <div className="flex items-center space-x-2 text-slate-300">
                      <span>✓</span>
                      <span>Calorías</span>
                    </div>
                    <div className="flex items-center space-x-2 text-slate-300">
                      <span>✓</span>
                      <span>Ruta GPS</span>
                    </div>
                    <div className="flex items-center space-x-2 text-slate-300">
                      <span>✓</span>
                      <span>Condiciones</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}
