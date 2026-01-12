/**
 * useAutoSync Hook
 * Sincroniza automáticamente datos de Garmin al hacer login y periódicamente
 */

import { useEffect, useRef, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/lib/auth-context';

const SYNC_INTERVAL = 6 * 60 * 60 * 1000; // 6 horas en milisegundos
const STORAGE_KEY = 'lastGarminSync';
const SYNCING_KEY = 'garminSyncing';

export function useAutoSync(forceOnMount: boolean = true) {
    const { userProfile } = useAuth();
    const syncingRef = useRef(false);
    const [isSyncing, setIsSyncing] = useState(false);
    
    // Solo sincronizar si el usuario tiene Garmin como dispositivo principal
    const shouldAttemptSync = userProfile?.primary_device === 'garmin';

    const shouldSync = (): boolean => {
        const lastSync = localStorage.getItem(STORAGE_KEY);

        if (!lastSync) {
            return true; // Never synced before
        }

        const lastSyncTime = new Date(lastSync).getTime();
        const now = Date.now();
        const timeSinceLastSync = now - lastSyncTime;

        return timeSinceLastSync >= SYNC_INTERVAL;
    };

    const performSync = async (force: boolean = false) => {
        // Solo intentar sincronizar si el usuario tiene Garmin
        if (!shouldAttemptSync) {
            console.log('[AutoSync] User does not have Garmin as primary device, skipping sync');
            return;
        }

        // Prevent multiple simultaneous syncs
        if (syncingRef.current) {
            console.log('[AutoSync] Sync already in progress, skipping');
            return;
        }

        if (!force && !shouldSync()) {
            console.log('[AutoSync] Last sync was recent, skipping');
            return;
        }

        try {
            syncingRef.current = true;
            setIsSyncing(true);
            localStorage.setItem(SYNCING_KEY, 'true');
            window.dispatchEvent(new Event('garmin-sync-started'));

            // First check if Garmin is connected before attempting sync
            try {
                const status = await apiClient.getGarminStatus();
                if (!status.connected) {
                    console.log('[AutoSync] Garmin not connected, skipping auto-sync');
                    // No retry for 24 hours
                    localStorage.setItem(STORAGE_KEY, new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString());
                    return;
                }
            } catch (statusError: any) {
                // Si hay error al verificar el status (ej: 401), no intentar sync
                console.log('[AutoSync] Error checking Garmin status, skipping sync:', statusError.response?.status || statusError.message);
                localStorage.setItem(STORAGE_KEY, new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString());
                return;
            }

            console.log('[AutoSync] Starting automatic sync...');

            // Try to sync
            const result = await apiClient.syncGarmin();

            // Update last sync time
            localStorage.setItem(STORAGE_KEY, new Date().toISOString());

            if (result.synced_count > 0) {
                console.log(`[AutoSync] Successfully synced ${result.synced_count} workouts`);

                window.dispatchEvent(new CustomEvent('garmin-sync-complete', {
                    detail: { count: result.synced_count }
                }));
            } else {
                console.log('[AutoSync] No new workouts to sync');
            }
        } catch (error: any) {
            // Si es 400 (Garmin no conectado) o 401 (no autenticado), no es un error crítico
            if (error.response?.status === 400 || error.response?.status === 401) {
                console.log('[AutoSync] Garmin not connected or not authenticated, skipping auto-sync');
                // No retry for 24 hours
                localStorage.setItem(STORAGE_KEY, new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString());
            } else {
                console.warn('[AutoSync] Failed to sync:', error.message);
            }
        } finally {
            syncingRef.current = false;
            setIsSyncing(false);
            localStorage.removeItem(SYNCING_KEY);
            window.dispatchEvent(new Event('garmin-sync-ended'));
        }
    };

    useEffect(() => {
        // Esperar a que userProfile esté cargado antes de intentar sincronizar
        if (!userProfile) {
            console.log('[AutoSync] Waiting for userProfile to load...');
            return;
        }

        // Solo sincronizar si el usuario tiene Garmin como dispositivo principal
        if (!shouldAttemptSync) {
            return;
        }

        // Always sync on mount (on login) - pero solo si no hay un sync reciente
        if (forceOnMount) {
            // Verificar si ya hay un sync muy reciente (menos de 1 minuto) para evitar múltiples syncs
            const lastSync = localStorage.getItem(STORAGE_KEY);
            if (lastSync) {
                const lastSyncTime = new Date(lastSync).getTime();
                const now = Date.now();
                const timeSinceLastSync = now - lastSyncTime;
                // Si la última sincronización fue hace menos de 1 minuto, no sincronizar de nuevo
                if (timeSinceLastSync < 60 * 1000) {
                    console.log('[AutoSync] Very recent sync detected, skipping mount sync');
                    return;
                }
            }
            performSync(true);
        }

        // Set up interval to check periodically (every 30 minutes)
        const checkInterval = setInterval(() => {
            performSync();
        }, 30 * 60 * 1000);

        return () => {
            clearInterval(checkInterval);
        };
    }, [userProfile, shouldAttemptSync, forceOnMount]);

    return {
        forceSync: performSync,
        shouldSync,
        isSyncing,
    };
}

/**
 * Manual trigger for sync with user feedback
 */
export async function manualSync(): Promise<{ success: boolean; count: number; message: string }> {
    try {
        const result = await apiClient.syncGarmin();

        // Update last sync time
        localStorage.setItem(STORAGE_KEY, new Date().toISOString());

        return {
            success: true,
            count: result.synced_count,
            message: `¡Sincronización exitosa! ${result.synced_count} entrenamientos nuevos.`
        };
    } catch (error: any) {
        return {
            success: false,
            count: 0,
            message: error.response?.data?.detail || 'Error al sincronizar'
        };
    }
}

/**
 * Get last sync time for display
 */
export function getLastSyncTime(): Date | null {
    const lastSync = localStorage.getItem(STORAGE_KEY);
    return lastSync ? new Date(lastSync) : null;
}

/**
 * Check if sync is currently in progress
 */
export function isSyncInProgress(): boolean {
    return localStorage.getItem(SYNCING_KEY) === 'true';
}

/**
 * Format time since last sync for display
 */
export function formatTimeSinceSync(): string {
    const lastSync = getLastSyncTime();

    if (!lastSync) {
        return 'Nunca sincronizado';
    }

    const now = Date.now();
    const diff = now - lastSync.getTime();

    const minutes = Math.floor(diff / (60 * 1000));
    const hours = Math.floor(diff / (60 * 60 * 1000));
    const days = Math.floor(diff / (24 * 60 * 60 * 1000));

    if (minutes < 1) {
        return 'Justo ahora';
    } else if (minutes < 60) {
        return `Hace ${minutes}min`;
    } else if (hours < 24) {
        return `Hace ${hours}h`;
    } else {
        return `Hace ${days}d`;
    }
}
