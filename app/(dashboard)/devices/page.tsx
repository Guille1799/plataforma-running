'use client';

import { DevicesList } from '@/components/DevicesList';

export default function DevicesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Mis Dispositivos</h1>
          <p className="text-lg text-gray-300">
            Administra tus dispositivos conectados y sincronización de datos
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-slate-800/50 backdrop-blur rounded-xl shadow-lg border border-slate-700 p-6">
          <DevicesList />
        </div>
      </div>
    </div>
  );
}
