'use client'

import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import { Button } from '@/components/ui/button'
import {
  Activity,
  BarChart3,
  MessageCircle,
  Settings,
  LogOut,
  Home,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/utils'

export function Sidebar() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  const menuItems = [
    {
      name: 'Home',
      href: '/dashboard',
      icon: Home,
      label: 'Dashboard',
    },
    {
      name: 'Workouts',
      href: '/dashboard/workouts',
      icon: Activity,
      label: 'Mis Entrenamientos',
    },
    {
      name: 'Analytics',
      href: '/dashboard/analytics',
      icon: BarChart3,
      label: 'Análisis',
    },
    {
      name: 'Coach',
      href: '/dashboard/coach',
      icon: MessageCircle,
      label: 'Coach AI',
    },
    {
      name: 'Training',
      href: '/dashboard/training',
      icon: Zap,
      label: 'Plan de Entrenamiento',
    },
    {
      name: 'Profile',
      href: '/dashboard/profile',
      icon: Settings,
      label: 'Perfil',
    },
  ]

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard'
    }
    return pathname.startsWith(href)
  }

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col h-screen sticky top-0">
      {/* Header */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
            <span className="font-bold text-white text-sm">RC</span>
          </div>
          <div>
            <h1 className="font-bold text-white">RunCoach</h1>
            <p className="text-xs text-slate-400">AI Platform</p>
          </div>
        </div>
      </div>

      {/* Menu */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.href)

          return (
            <Link key={item.href} href={item.href}>
              <div
                className={cn(
                  'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
                  'hover:bg-slate-800 cursor-pointer',
                  active
                    ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/20'
                    : 'text-slate-400 hover:text-white'
                )}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                <span className="font-medium">{item.label}</span>
                {active && (
                  <div className="ml-auto w-2 h-2 bg-cyan-400 rounded-full" />
                )}
              </div>
            </Link>
          )
        })}
      </nav>

      {/* User Section */}
      <div className="border-t border-slate-800 p-4 space-y-3">
        {user && (
          <div className="bg-slate-900/50 rounded-lg p-3">
            <p className="text-xs text-slate-400">Usuario</p>
            <p className="text-sm font-medium text-white truncate">{user.email}</p>
          </div>
        )}
        <Button
          onClick={handleLogout}
          variant="outline"
          size="sm"
          className="w-full border-slate-700 hover:bg-slate-800"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Logout
        </Button>
      </div>
    </aside>
  )
}
