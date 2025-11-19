'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import Sidebar from '@/components/Sidebar';

export default function WorkoutsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter();
  const { isLoading } = useAuth();

  useEffect(() => {
    // Si no hay token, redirigir a login
    const token = localStorage.getItem('auth_token');
    if (!token && !isLoading) {
      router.push('/login');
    }
  }, [isLoading, router]);

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
        <div className="text-white">Cargando...</div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0">
        <Sidebar />
      </aside>
      
      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  )
}
