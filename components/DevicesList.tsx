'use client';

import { useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import { DeviceCard } from './DeviceCard';
import { AddDeviceModal } from './AddDeviceModal';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/lib/toast-context';
import { AlertCircle, Plus, Zap } from 'lucide-react';

export function DevicesList() {
  const [showAddModal, setShowAddModal] = useState(false);
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  // Fetch devices
  const { data: devicesData, isLoading, error } = useQuery({
    queryKey: ['integrations'],
    queryFn: () => apiClient.getDeviceIntegrations(),
    refetchInterval: 30000, // Refetch every 30s
  });

  // Add device mutation
  const addDeviceMutation = useMutation({
    mutationFn: (data: any) => apiClient.addDeviceIntegration(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      showToast('Dispositivo agregado exitosamente', 'success');
      setShowAddModal(false);
    },
    onError: (error: any) => {
      showToast(
        error.response?.data?.detail || 'Error al agregar dispositivo',
        'error'
      );
    },
  });

  // Remove device mutation
  const removeDeviceMutation = useMutation({
    mutationFn: (deviceId: string) => apiClient.removeDeviceIntegration(deviceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      showToast('Dispositivo eliminado', 'success');
    },
    onError: (error: any) => {
      showToast(
        error.response?.data?.detail || 'Error al eliminar dispositivo',
        'error'
      );
    },
  });

  // Update device mutation
  const updateDeviceMutation = useMutation({
    mutationFn: ({ deviceId, data }: any) =>
      apiClient.updateDeviceIntegration(deviceId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      showToast('Dispositivo actualizado', 'success');
    },
    onError: (error: any) => {
      showToast(
        error.response?.data?.detail || 'Error al actualizar dispositivo',
        'error'
      );
    },
  });

  // Set primary device mutation
  const setPrimaryMutation = useMutation({
    mutationFn: (deviceId: string) => apiClient.setPrimaryDevice(deviceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      showToast('Dispositivo primario actualizado', 'success');
    },
    onError: (error: any) => {
      showToast(
        error.response?.data?.detail || 'Error al actualizar dispositivo primario',
        'error'
      );
    },
  });

  // Sync all mutation
  const syncAllMutation = useMutation({
    mutationFn: () => apiClient.syncAllDevices(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      showToast('Sincronización iniciada', 'success');
    },
    onError: (error: any) => {
      showToast(
        error.response?.data?.detail || 'Error al sincronizar',
        'error'
      );
    },
  });

  const devices = devicesData?.devices || [];
  const syncEnabled = devicesData?.devices_enabled || false;
  const primaryDevice = devicesData?.primary_device || 'manual';

  const isAnyMutationLoading =
    addDeviceMutation.isPending ||
    removeDeviceMutation.isPending ||
    updateDeviceMutation.isPending ||
    setPrimaryMutation.isPending;

  const handleAddDevice = async (formData: any) => {
    await addDeviceMutation.mutateAsync(formData);
  };

  const handleDeleteDevice = (deviceId: string) => {
    removeDeviceMutation.mutate(deviceId);
  };

  const handleSetPrimary = (deviceId: string) => {
    setPrimaryMutation.mutate(deviceId);
  };

  const handleEditDevice = (device: any) => {
    // TODO: Implement edit device modal
    console.log('Edit device:', device);
  };

  const handleSyncAll = () => {
    syncAllMutation.mutate();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner className="w-8 h-8" />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-6 border-red-200 bg-red-50">
        <div className="flex gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
          <div>
            <h3 className="font-semibold text-red-900 mb-1">Error al cargar dispositivos</h3>
            <p className="text-sm text-red-800">
              No pudimos cargar tus dispositivos. Por favor intenta nuevamente.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Master Sync Control */}
      <Card className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 text-white rounded-lg">
              <Zap size={20} />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Sincronización Automática</h3>
              <p className="text-sm text-gray-600">
                {syncEnabled
                  ? 'Tus dispositivos se sincronizan automáticamente'
                  : 'Sincronización desactivada'}
              </p>
            </div>
          </div>
          {devices.length > 0 && (
            <Button
              onClick={handleSyncAll}
              disabled={isAnyMutationLoading || syncAllMutation.isPending}
              variant={syncAllMutation.isPending ? 'outline' : 'default'}
            >
              {syncAllMutation.isPending ? 'Sincronizando...' : 'Sincronizar Ahora'}
            </Button>
          )}
        </div>
      </Card>

      {/* Devices List Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Mis Dispositivos</h2>
          <p className="text-sm text-gray-600 mt-1">
            {devices.length === 0
              ? 'No tienes dispositivos configurados'
              : `${devices.length} dispositivo${devices.length !== 1 ? 's' : ''} configurado${devices.length !== 1 ? 's' : ''}`}
          </p>
        </div>
        <Button onClick={() => setShowAddModal(true)} disabled={isAnyMutationLoading}>
          <Plus size={18} className="mr-2" /> Agregar Dispositivo
        </Button>
      </div>

      {/* Devices Grid */}
      {devices.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {devices.map((device: any) => (
            <DeviceCard
              key={device.device_id}
              device={device}
              onEdit={handleEditDevice}
              onDelete={handleDeleteDevice}
              onSetPrimary={handleSetPrimary}
              isLoading={isAnyMutationLoading}
            />
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center border-dashed">
          <div className="text-5xl mb-4">📱</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Sin dispositivos</h3>
          <p className="text-gray-600 mb-6 max-w-sm mx-auto">
            Agrega tu primer dispositivo para comenzar a sincronizar tus entrenamientos
          </p>
          <Button onClick={() => setShowAddModal(true)}>Agregar Primer Dispositivo</Button>
        </Card>
      )}

      {/* Add Device Modal */}
      <AddDeviceModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={handleAddDevice}
        isLoading={isAnyMutationLoading}
      />
    </div>
  );
}
