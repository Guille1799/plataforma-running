'use client'

import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function TrainingPage() {
  const { isAuthenticated, user } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, router])

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Redirecting to login...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* User Welcome */}
        {user && (
          <div className="mb-6 p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg">
            <p className="text-sm text-gray-300">
              Welcome back, <span className="font-semibold text-purple-400">{user.email}</span>! 🏃
            </p>
          </div>
        )}

        {/* Training Page - Coming Soon */}
        <div className="p-8 text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Training Dashboard</h1>
          <p className="text-gray-400">Training features coming soon...</p>
        </div>
      </div>
    </div>
  )
}
