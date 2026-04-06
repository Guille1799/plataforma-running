'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { useAutoSync } from '@/hooks/useAutoSync';
import Sidebar from '@/components/Sidebar';
import Navbar from '@/components/Navbar';
import { DemoTour } from '@/components/DemoTour';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter();
  const { isLoading } = useAuth();

  // Auto-sync Garmin data every 6 hours
  useAutoSync();

  useEffect(() => {
    // Redirect to login if no token present
    const token = localStorage.getItem('auth_token');
    if (!token && !isLoading) {
      router.push('/login');
    }
  }, [isLoading, router]);

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-950">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-slate-800 border-t-blue-500 rounded-full animate-spin" />
          <p className="text-slate-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-slate-950">
      <DemoTour />
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 border-r border-slate-800">
        <Sidebar />
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Navbar */}
        <Navbar />

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6">
            {children}
          </div>
        </div>
      </main>
    </div>
  )
}