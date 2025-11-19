'use client'

import { useAuth } from '@/lib/auth-context'
import { Bell, LogOut, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function Navbar() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout error:', error)
      setIsLoggingOut(false)
    }
  }

  return (
    <nav className="border-b border-slate-800 bg-slate-950 h-16 flex items-center justify-between px-6">
      {/* Left - Search */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-500" />
          <Input
            placeholder="Buscar entrenamientos..."
            className="pl-10 bg-slate-900 border-slate-800 focus:border-blue-500 text-sm"
          />
        </div>
      </div>

      {/* Right - Actions */}
      <div className="flex items-center gap-6 ml-auto">
        {/* Notifications */}
        <button className="relative hover:text-blue-400 transition-colors">
          <Bell className="w-5 h-5 text-slate-400" />
          <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        {/* User Info */}
        {user && (
          <div className="flex items-center gap-3 pl-6 border-l border-slate-800">
            <div className="text-right text-sm">
              <p className="text-white font-medium">{user.email?.split('@')[0]}</p>
              <p className="text-xs text-slate-400">{user.email}</p>
            </div>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <span className="text-xs font-bold text-white">
                {user.email?.[0].toUpperCase()}
              </span>
            </div>
          </div>
        )}

        {/* Logout Button */}
        <Button
          onClick={handleLogout}
          disabled={isLoggingOut}
          variant="ghost"
          size="sm"
          className="ml-4 hover:bg-slate-800 text-slate-400 hover:text-white"
        >
          <LogOut className="w-4 h-4 mr-2" />
          {isLoggingOut ? 'Saliendo...' : 'Logout'}
        </Button>
      </div>
    </nav>
  )
}