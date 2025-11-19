'use client';

/**
 * Dashboard Page - Adaptive layout based on device preference
 */
import { useAuth } from '@/lib/auth-context';
import { useDashboardLayout } from '@/lib/useDashboardLayout';
import { Spinner } from '@/components/ui/spinner';

export default function DashboardPage() {
  const { user, isLoading, onboardingCompleted } = useAuth();
  const { primaryDevice, DashboardComponent } = useDashboardLayout();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <Spinner />
      </div>
    );
  }

  if (!onboardingCompleted) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="text-center">
          <p className="text-white text-lg mb-4">Completing your setup...</p>
          <Spinner />
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="fixed top-4 right-4 px-3 py-1 bg-slate-800/50 rounded-lg text-xs text-slate-400 border border-slate-600 backdrop-blur">
        Device: <span className="capitalize text-slate-300 font-semibold">{primaryDevice}</span>
      </div>
      <DashboardComponent />
    </>
  );
}

