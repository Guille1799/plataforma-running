'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Notification {
  id: string;
  type: 'reminder' | 'achievement' | 'tip';
  title: string;
  message: string;
  icon: string;
  enabled: boolean;
}

export function NotificationSettings() {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      type: 'reminder',
      title: 'Recordatorio de Entrenamiento',
      message: 'Recibe notificaciones sobre tu próximo entrenamiento programado',
      icon: '📅',
      enabled: true,
    },
    {
      id: '2',
      type: 'reminder',
      title: 'Resumen Semanal',
      message: 'Resumen de tu desempeño cada domingo a las 20:00',
      icon: '📊',
      enabled: true,
    },
    {
      id: '3',
      type: 'achievement',
      title: 'Logros Desbloqueados',
      message: 'Notificaciones cuando alcances nuevos hitos y récords',
      icon: '🏆',
      enabled: true,
    },
    {
      id: '4',
      type: 'tip',
      title: 'Consejos de Entrenamiento',
      message: 'Recibe recomendaciones personalizadas del Coach AI',
      icon: '💡',
      enabled: false,
    },
    {
      id: '5',
      type: 'reminder',
      title: 'Sincronización Garmin',
      message: 'Recordatorio para sincronizar tu dispositivo Garmin',
      icon: '🔄',
      enabled: true,
    },
  ]);

  const [testNotification, setTestNotification] = useState(false);

  const toggleNotification = (id: string) => {
    setNotifications(prev =>
      prev.map(n =>
        n.id === id ? { ...n, enabled: !n.enabled } : n
      )
    );
  };

  const sendTestNotification = async () => {
    setTestNotification(true);
    setTimeout(() => setTestNotification(false), 3000);

    // Try to send notification if browser supports it
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('RunCoach AI', {
        body: '✅ Notificación de prueba enviada correctamente',
        icon: '🏃',
      });
    }
  };

  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        sendTestNotification();
      } else if (Notification.permission !== 'denied') {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
          sendTestNotification();
        }
      }
    }
  };

  const enabledCount = notifications.filter(n => n.enabled).length;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">🔔 Centro de Notificaciones</h2>

      {/* Summary */}
      <Card className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 border-blue-700">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-300 mb-1">Notificaciones Activas</p>
              <p className="text-3xl font-bold text-blue-400">{enabledCount}</p>
            </div>
            <div className="text-5xl">🔔</div>
          </div>
          <p className="text-xs text-blue-200 mt-3">
            Tienes {enabledCount} de {notifications.length} notificaciones habilitadas
          </p>
        </CardContent>
      </Card>

      {/* Notification List */}
      <div className="space-y-3">
        {notifications.map(notification => (
          <Card key={notification.id} className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="text-2xl mt-1">{notification.icon}</div>
                  <div>
                    <h4 className="font-semibold text-white">{notification.title}</h4>
                    <p className="text-sm text-slate-400 mt-1">{notification.message}</p>
                    <p className="text-xs text-slate-500 mt-2">
                      {notification.type === 'reminder' && '📅 Recordatorio'}
                      {notification.type === 'achievement' && '🏆 Logros'}
                      {notification.type === 'tip' && '💡 Consejos'}
                    </p>
                  </div>
                </div>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notification.enabled}
                    onChange={() => toggleNotification(notification.id)}
                    className="w-5 h-5 rounded accent-blue-600"
                  />
                </label>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Test Notification */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-lg">🧪 Prueba de Notificación</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-300">
            Envíate una notificación de prueba para verificar que todo funciona correctamente.
          </p>
          <button
            onClick={requestNotificationPermission}
            className={`w-full px-4 py-3 rounded-lg font-medium transition-all ${
              testNotification
                ? 'bg-green-600 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {testNotification ? '✓ ¡Notificación enviada!' : '📬 Enviar Notificación de Prueba'}
          </button>
          <p className="text-xs text-slate-400">
            Se te pedirá permiso para enviar notificaciones la primera vez.
          </p>
        </CardContent>
      </Card>

      {/* Quick Settings */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-lg">⚙️ Ajustes Rápidos</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <button
            onClick={() => {
              setNotifications(prev =>
                prev.map(n => ({ ...n, enabled: true }))
              );
            }}
            className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors text-sm"
          >
            ✓ Habilitar Todas
          </button>
          <button
            onClick={() => {
              setNotifications(prev =>
                prev.map(n => ({ ...n, enabled: false }))
              );
            }}
            className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors text-sm"
          >
            ✕ Deshabilitar Todas
          </button>
        </CardContent>
      </Card>

      {/* Info */}
      <div className="p-4 bg-blue-900/30 border border-blue-700 rounded-lg text-sm text-blue-200">
        <p className="mb-2">ℹ️ Información</p>
        <ul className="space-y-1 text-xs list-disc list-inside">
          <li>Las notificaciones requieren permiso del navegador</li>
          <li>Puedes cambiar los ajustes de notificaciones en cualquier momento</li>
          <li>Los recordatorios se enviarán según tus entrenamientos programados</li>
          <li>Los logros se desbloquean automáticamente cuando alcanzas los hitos</li>
        </ul>
      </div>
    </div>
  );
}
