'use client';

import { useEffect, useState } from 'react';
import { formatTimeSinceSync, getLastSyncTime, isSyncInProgress } from '@/hooks/useAutoSync';

export function SyncIndicator() {
    const [syncing, setSyncing] = useState(false);
    const [lastSync, setLastSync] = useState<string>('');

    useEffect(() => {
        // Initial state
        setSyncing(isSyncInProgress());
        setLastSync(formatTimeSinceSync());

        // Update time display every minute
        const interval = setInterval(() => {
            setLastSync(formatTimeSinceSync());
        }, 60000);

        // Listen for sync events
        const handleSyncStart = () => {
            setSyncing(true);
        };

        const handleSyncEnd = () => {
            setSyncing(false);
            setLastSync(formatTimeSinceSync());
        };

        const handleSyncComplete = () => {
            setSyncing(false);
            setLastSync('Justo ahora');
        };

        window.addEventListener('garmin-sync-started', handleSyncStart);
        window.addEventListener('garmin-sync-ended', handleSyncEnd);
        window.addEventListener('garmin-sync-complete', handleSyncComplete);

        return () => {
            clearInterval(interval);
            window.removeEventListener('garmin-sync-started', handleSyncStart);
            window.removeEventListener('garmin-sync-ended', handleSyncEnd);
            window.removeEventListener('garmin-sync-complete', handleSyncComplete);
        };
    }, []);

    const lastSyncTime = getLastSyncTime();

    // Don't show if never synced
    if (!lastSyncTime && !syncing) {
        return null;
    }

    return (
        <div className="flex items-center gap-2 text-xs text-slate-400">
            <div className="flex items-center gap-1.5">
                {syncing ? (
                    <>
                        <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                        <span className="text-blue-400">Sincronizando...</span>
                    </>
                ) : (
                    <>
                        <div className="w-2 h-2 rounded-full bg-green-500" />
                        <span>Última sincronización: {lastSync}</span>
                    </>
                )}
            </div>
        </div>
    );
}
