/**
 * useAutoSync Hook
 * Sincroniza automáticamente datos de Garmin al hacer login y periódicamente
 */

import { useEffect, useRef, useState } from 'react';
import { apiClient } from '@/lib/api-client';

const SYNC_INTERVAL = 6 * 60 * 60 * 1000; // 6 horas en milisegundos
const STORAGE_KEY = 'lastGarminSync';
const SYNCING_KEY = 'garminSyncing';

export function useAutoSync(forceOnMount: boolean = true) {
    const syncingRef = useRef(false);
    const [isSyncing, setIsSyncing] = useState(false);

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

            console.log('[AutoSync] Starting automatic sync...');

            // Try to sync
            const result = await apiClient.syncGarmin();

            // Update last sync time
            localStorage.setItem(STORAGE_KEY, new Date().toISOString());

            // Backend returns workouts_synced; fall back to synced_count for compatibility
            const count = result.workouts_synced ?? result.synced_count ?? 0;

            if (count > 0) {
                console.log(`[AutoSync] Successfully synced ${count} workouts`);
                window.dispatchEvent(new CustomEvent('garmin-sync-complete', {
                    detail: { count }
                }));
            } else {
                console.log('[AutoSync] No new workouts to sync');
            }
        } catch (error: any) {
            console.warn('[AutoSync] Failed to sync:', error.message);

            // If it's a 401 (not authenticated), don't retry soon
            if (error.response?.status === 401) {
                console.log('[AutoSync] Not authenticated, will not auto-sync again');
                localStorage.setItem(STORAGE_KEY, new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString());
            }
        } finally {
            syncingRef.current = false;
            setIsSyncing(false);
            localStorage.removeItem(SYNCING_KEY);
            window.dispatchEvent(new Event('garmin-sync-ended'));
        }
    };

    useEffect(() => {
        // Always sync on mount (on login)
        if (forceOnMount) {
            performSync(true);
        }

        // Set up interval to check periodically (every 30 minutes)
        const checkInterval = setInterval(() => {
            performSync();
        }, 30 * 60 * 1000);

        return () => {
            clearInterval(checkInterval);
        };
    }, []);

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

        const count = result.workouts_synced ?? result.synced_count ?? 0;

        return {
            success: true,
            count,
            message: count > 0
                ? `Sync complete! ${count} new workout${count === 1 ? '' : 's'} imported.`
                : 'Sync complete. No new workouts since last sync.',
        };
    } catch (error: any) {
        const status: number | undefined = error.response?.status;
        const detail: string | undefined = error.response?.data?.detail;

        let message = detail || error.message || 'Sync failed. Check your connection and try again.';

        if (status === 429) {
            message = 'Garmin is rate-limiting requests. Wait a few minutes and try again.';
        } else if (status === 401) {
            message = 'Invalid Garmin credentials. Reconnect your account in the Garmin tab.';
        } else if (status === 400 && !detail) {
            message = 'Garmin account not connected. Connect your account first.';
        }

        return { success: false, count: 0, message };
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
        return 'Never synced';
    }

    const now = Date.now();
    const diff = now - lastSync.getTime();

    const minutes = Math.floor(diff / (60 * 1000));
    const hours = Math.floor(diff / (60 * 60 * 1000));
    const days = Math.floor(diff / (24 * 60 * 60 * 1000));

    if (minutes < 1) {
        return 'Just now';
    } else if (minutes < 60) {
        return `${minutes}min ago`;
    } else if (hours < 24) {
        return `${hours}h ago`;
    } else {
        return `${days}d ago`;
    }
}
