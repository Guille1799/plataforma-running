'use client'

import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api-client'
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react'

export default function GoogleFitCallbackPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('Conectando con Google Fit...')

  const callbackMutation = useMutation({
    mutationFn: async ({ code, state }: { code: string; state: string }) => {
      return apiClient.googleFitCallback(code, state)
    },
    onSuccess: () => {
      setStatus('success')
      setMessage('✅ Google Fit conectado exitosamente')
      // Redirect to health page after 2 seconds
      setTimeout(() => {
        router.push('/health/devices')
      }, 2000)
    },
    onError: (error: any) => {
      setStatus('error')
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
    },
  })

  useEffect(() => {
    const code = searchParams.get('code')
    const state = searchParams.get('state')
    const error = searchParams.get('error')

    if (error) {
      setStatus('error')
      setMessage(`❌ Error de autorización: ${error}`)
      return
    }

    if (code && state) {
      callbackMutation.mutate({ code, state })
    } else {
      setStatus('error')
      setMessage('❌ Parámetros de autorización inválidos')
    }
  }, [searchParams])

  return (
    <div className="flex items-center justify-center min-h-screen p-6">
      <Card className="max-w-md w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {status === 'loading' && <Loader2 className="h-5 w-5 animate-spin" />}
            {status === 'success' && <CheckCircle2 className="h-5 w-5 text-green-500" />}
            {status === 'error' && <XCircle className="h-5 w-5 text-red-500" />}
            Google Fit Connection
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-lg">{message}</p>
          {status === 'success' && (
            <p className="text-sm text-muted-foreground text-center mt-4">
              Redirigiendo en 2 segundos...
            </p>
          )}
          {status === 'error' && (
            <div className="mt-4 text-center">
              <a href="/health/devices" className="text-blue-500 hover:underline">
                Volver a intentar →
              </a>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
