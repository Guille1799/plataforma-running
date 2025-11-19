'use client';

import { useAuth } from '@/lib/auth-context';
import { usePathname, useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: '📊',
  },
  {
    name: 'Health Metrics',
    href: '/health',
    icon: '❤️',
    submenu: [
      { name: 'Dashboard', href: '/health' },
      { name: 'Historial', href: '/health/history' },
      { name: 'Dispositivos', href: '/health/devices' },
    ]
  },
  {
    name: 'Entrenamientos',
    href: '/workouts',
    icon: '🏃',
  },
  {
    name: 'Planes',
    href: '/training-plans',
    icon: '📅',
  },
  {
    name: 'Predicciones',
    href: '/predictions',
    icon: '🎯',
  },
  {
    name: 'Dispositivos',
    href: '/devices',
    icon: '📱',
  },
  {
    name: 'Subir Archivo',
    href: '/upload',
    icon: '📤',
  },
  {
    name: 'Coach AI',
    href: '/coach',
    icon: '💬',
  },
  {
    name: 'Integraciones',
    href: '/garmin',
    icon: '🔗',
  },
  {
    name: 'Perfil',
    href: '/profile',
    icon: '👤',
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  return (
    <div className="flex flex-col h-full bg-slate-900/50 border-r border-slate-700 backdrop-blur">
      {/* Logo / Brand */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <span className="text-2xl">⚡</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">RunCoach</h1>
            <p className="text-xs text-slate-400">AI Training</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <button
              key={item.name}
              onClick={() => router.push(item.href)}
              className={cn(
                'w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all',
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/50'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              )}
            >
              <span className="text-2xl">{item.icon}</span>
              <span className="font-medium">{item.name}</span>
            </button>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-slate-700">
        <div className="flex items-center space-x-3 px-4 py-3 bg-slate-800/50 rounded-lg mb-2">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-green-500 to-blue-600 flex items-center justify-center text-white font-semibold">
            {user?.email?.[0].toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">
              {user?.email?.split('@')[0] || 'Usuario'}
            </p>
            <p className="text-xs text-slate-400 truncate">
              {user?.email || ''}
            </p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition-colors"
        >
          <span>🚪</span>
          <span className="text-sm font-medium">Cerrar Sesión</span>
        </button>
      </div>
    </div>
  );
}
