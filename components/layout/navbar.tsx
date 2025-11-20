'use client'

import { useAuth } from '@/lib/auth-context'
import { Bell, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export function Navbar() {
  const { user } = useAuth()

  return (
    <nav className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-40">
      <div className="flex items-center justify-between h-16 px-6">
        {/* Left - Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-500" />
            <Input
              placeholder="Buscar entrenamientos..."
              className="pl-10 bg-slate-900 border-slate-800 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Right - Actions */}
        <div className="flex items-center gap-4 ml-auto">
          {/* Notifications */}
          <Button
            variant="ghost"
            size="icon"
            className="relative hover:bg-slate-800"
          >
            <Bell className="w-5 h-5 text-slate-400" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full" />
          </Button>

          {/* User Menu */}
          <Button
            variant="ghost"
            size="icon"
            className="hover:bg-slate-800"
            title={user?.email || 'User'}
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <span className="text-xs font-bold text-white">
                {user?.email?.[0].toUpperCase()}
              </span>
            </div>
          </Button>
        </div>
      </div>
    </nav>
  )
}
