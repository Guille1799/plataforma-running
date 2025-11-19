/**
 * useDashboardLayout.ts - Hook para seleccionar el dashboard correcto según device
 */
import { useAuth } from '@/lib/auth-context';
import { GarminDashboard } from '@/components/dashboards/GarminDashboard';
import { XiaomiDashboard } from '@/components/dashboards/XiaomiDashboard';
import { ManualDashboard } from '@/components/dashboards/ManualDashboard';

export function useDashboardLayout() {
  const { userProfile } = useAuth();

  const primaryDevice = userProfile?.primary_device || 'manual';

  const getDashboardComponent = () => {
    switch (primaryDevice) {
      case 'garmin':
        return GarminDashboard;
      case 'xiaomi':
        return XiaomiDashboard;
      case 'apple':
        return ManualDashboard; // Apple Health users get manual layout for now
      case 'strava':
        return ManualDashboard; // Strava users get manual layout
      case 'manual':
      default:
        return ManualDashboard;
    }
  };

  return {
    primaryDevice,
    DashboardComponent: getDashboardComponent(),
  };
}
