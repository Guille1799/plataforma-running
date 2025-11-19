'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';

interface AddDeviceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (data: {
    device_type: string;
    device_name: string;
    sync_interval_hours: number;
    auto_sync_enabled: boolean;
  }) => void;
  isLoading?: boolean;
  onOpenChange?: (open: boolean) => void;
}

const deviceTypes = [
  { value: 'garmin', label: 'Garmin', icon: '⌚', description: 'Reloj deportivo Garmin' },
  { value: 'xiaomi', label: 'Xiaomi', icon: '📱', description: 'Pulsera/Reloj Xiaomi' },
  { value: 'strava', label: 'Strava', icon: '🏃', description: 'Aplicación Strava' },
  { value: 'apple', label: 'Apple Health', icon: '🍎', description: 'Apple Health' },
  { value: 'manual', label: 'Entrada Manual', icon: '✍️', description: 'Registros manuales' },
];

export function AddDeviceModal({ isOpen, onClose, onAdd, isLoading = false }: AddDeviceModalProps) {
  const [selectedType, setSelectedType] = useState('garmin');
  const [deviceName, setDeviceName] = useState('');
  const [syncInterval, setSyncInterval] = useState(1);
  const [autoSync, setAutoSync] = useState(true);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!deviceName.trim()) {
      setError('Por favor ingresa un nombre para el dispositivo');
      return;
    }

    try {
      setIsSubmitting(true);
      await onAdd({
        device_type: selectedType,
        device_name: deviceName.trim(),
        sync_interval_hours: syncInterval,
        auto_sync_enabled: autoSync,
      });

      // Reset form
      setDeviceName('');
      setSyncInterval(1);
      setAutoSync(true);
      setSelectedType('garmin');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al agregar dispositivo');
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedTypeConfig = deviceTypes.find((t) => t.value === selectedType);

  return (
    <Dialog open={isOpen} onOpenChange={(open: boolean) => !open && onClose()}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Agregar Nuevo Dispositivo</DialogTitle>
        </DialogHeader>
        <DialogDescription className="text-sm text-gray-600 px-6">
          Conecta un nuevo dispositivo para sincronizar tus entrenamientos
        </DialogDescription>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Device Type Selection */}
          <div className="space-y-3">
            <Label>Tipo de Dispositivo</Label>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
              {deviceTypes.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setSelectedType(type.value)}
                  className={`p-3 rounded-lg border-2 transition-all text-center ${
                    selectedType === type.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-1">{type.icon}</div>
                  <div className="text-xs font-semibold">{type.label}</div>
                  <div className="text-xs text-gray-600 truncate">{type.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Device Name */}
          <div className="space-y-2">
            <Label htmlFor="deviceName">Nombre del Dispositivo</Label>
            <Input
              id="deviceName"
              placeholder={selectedTypeConfig ? selectedTypeConfig.label : 'Mi dispositivo'}
              value={deviceName}
              onChange={(e) => setDeviceName(e.target.value)}
              disabled={isSubmitting || isLoading}
              maxLength={50}
            />
            <p className="text-xs text-gray-500">{deviceName.length}/50 caracteres</p>
          </div>

          {/* Sync Interval */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Intervalo de Sincronización</Label>
              <span className="text-lg font-semibold text-blue-600">{syncInterval}h</span>
            </div>
            <Slider
              min={1}
              max={24}
              step={1}
              value={[syncInterval]}
              onValueChange={(value) => setSyncInterval(value[0])}
              disabled={isSubmitting || isLoading}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-600">
              <span>Cada hora</span>
              <span>Cada día</span>
            </div>
          </div>

          {/* Auto Sync Toggle */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium text-sm">Sincronización Automática</p>
              <p className="text-xs text-gray-600">
                {autoSync
                  ? 'Se sincronizará automáticamente'
                  : 'Solo sincroniza manualmente'}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setAutoSync(!autoSync)}
              disabled={isSubmitting || isLoading}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                autoSync ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  autoSync ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 justify-end pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting || isLoading}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={isSubmitting || isLoading}>
              {isSubmitting ? 'Agregando...' : 'Agregar Dispositivo'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
