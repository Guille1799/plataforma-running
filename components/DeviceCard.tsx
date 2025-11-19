'use client';

import { useState } from 'react';
import { Trash2, Edit2, Star, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface DeviceCardProps {
  device: {
    device_id: string;
    device_type: string;
    device_name: string;
    is_primary: boolean;
    sync_config: {
      sync_interval_hours: number;
      auto_sync_enabled: boolean;
      last_sync: string | null;
      next_sync: string | null;
    };
    connected_at: string;
  };
  onEdit?: (device: any) => void;
  onDelete?: (deviceId: string) => void;
  onSetPrimary?: (deviceId: string) => void;
  isLoading?: boolean;
}

const deviceTypeConfig: Record<string, { color: string; label: string; icon: string }> = {
  garmin: { color: 'bg-blue-500', label: 'Garmin', icon: '⌚' },
  xiaomi: { color: 'bg-orange-500', label: 'Xiaomi', icon: '📱' },
  strava: { color: 'bg-orange-600', label: 'Strava', icon: '🏃' },
  apple: { color: 'bg-gray-800', label: 'Apple Health', icon: '🍎' },
  manual: { color: 'bg-green-600', label: 'Manual', icon: '✍️' },
};

export function DeviceCard({
  device,
  onEdit,
  onDelete,
  onSetPrimary,
  isLoading = false,
}: DeviceCardProps) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const config = deviceTypeConfig[device.device_type] || deviceTypeConfig.manual;

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Nunca';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Ahora mismo';
    if (diffMins < 60) return `Hace ${diffMins} min`;
    if (diffHours < 24) return `Hace ${diffHours}h`;
    if (diffDays < 7) return `Hace ${diffDays}d`;
    return date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' });
  };

  return (
    <Card className="overflow-hidden border-l-4" style={{ borderLeftColor: 'var(--device-color)' }}>
      <style>{`
        :root {
          --device-color: ${
            device.device_type === 'garmin'
              ? '#3b82f6'
              : device.device_type === 'xiaomi'
                ? '#f97316'
                : device.device_type === 'strava'
                  ? '#ea580c'
                  : device.device_type === 'apple'
                    ? '#1f2937'
                    : '#16a34a'
          };
        }
      `}</style>
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-3 flex-1">
            <div className={`${config.color} text-white rounded-lg p-2 text-xl`}>
              {config.icon}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-base truncate text-white">{device.device_name}</h3>
                {device.is_primary && (
                  <span className="inline-flex items-center gap-1 bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap">
                    <Star size={12} className="fill-yellow-800" /> Primario
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-300">{config.label}</p>
            </div>
          </div>

          {/* Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger>
              <button
                className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-gray-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 disabled:pointer-events-none disabled:opacity-50 h-9 px-3 text-gray-300"
                disabled={isLoading}
              >
                <MoreVertical size={16} />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onEdit?.(device)}>
                <Edit2 size={14} className="mr-2" /> Editar
              </DropdownMenuItem>
              {!device.is_primary && (
                <DropdownMenuItem onClick={() => onSetPrimary?.(device.device_id)}>
                  <Star size={14} className="mr-2" /> Establecer como primario
                </DropdownMenuItem>
              )}
              <DropdownMenuItem
                className="text-red-600"
                onClick={() => setShowDeleteConfirm(true)}
              >
                <Trash2 size={14} className="mr-2" /> Eliminar
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Sync Config */}
        <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b border-gray-700">
          <div>
            <p className="text-xs text-gray-400 mb-1">Intervalo de sincronización</p>
            <p className="text-sm font-semibold text-white">{device.sync_config.sync_interval_hours}h</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-1">Auto-sincronización</p>
            <p className="text-sm font-semibold text-white">
              {device.sync_config.auto_sync_enabled ? '✓ Activada' : '✗ Desactivada'}
            </p>
          </div>
        </div>

        {/* Last Sync */}
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div>
            <p className="text-gray-400 mb-1">Última sincronización</p>
            <p className="font-medium text-gray-200">{formatDate(device.sync_config.last_sync)}</p>
          </div>
          <div>
            <p className="text-gray-400 mb-1">Próxima sincronización</p>
            <p className="font-medium text-gray-200">{formatDate(device.sync_config.next_sync)}</p>
          </div>
        </div>

        {/* Delete Confirmation */}
        {showDeleteConfirm && (
          <div className="mt-4 p-3 bg-red-50 rounded-lg border border-red-200">
            <p className="text-sm mb-3 text-gray-700">¿Eliminar {device.device_name}?</p>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="destructive"
                onClick={() => {
                  onDelete?.(device.device_id);
                  setShowDeleteConfirm(false);
                }}
                disabled={isLoading}
              >
                Eliminar
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isLoading}
              >
                Cancelar
              </Button>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
