'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import Link from 'next/link';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Sparkles, Copy, Check } from 'lucide-react';
import { toast } from 'sonner';

const DEMO_EMAIL = process.env.NEXT_PUBLIC_DEMO_EMAIL?.trim() ?? '';
const DEMO_PASSWORD = process.env.NEXT_PUBLIC_DEMO_PASSWORD ?? '';
const hasDemoCredentials = Boolean(DEMO_EMAIL && DEMO_PASSWORD);

function mapLoginError(err: unknown): string {
  const e = err as {
    code?: string;
    message?: string;
    response?: { status?: number; data?: { detail?: unknown } };
  };
  if (e.code === 'ERR_NETWORK' || e.message?.includes('Network Error')) {
    return 'Cannot reach the server. Is the backend running?';
  }
  if (e.response?.status === 404) {
    return 'No account found for this email. Want to sign up?';
  }
  if (e.response?.status === 401) {
    return 'Wrong email or password. Try again.';
  }
  if (e.response?.status === 422) {
    const detail = e.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    return 'Invalid data. Check your email and password.';
  }
  const detail = e.response?.data?.detail;
  return typeof detail === 'string' ? detail : 'Something went wrong. Please try again.';
}

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedField, setCopiedField] = useState<'email' | 'password' | null>(null);

  const runLogin = async (emailVal: string, passwordVal: string) => {
    if (!emailVal || !passwordVal) {
      setError('Please fill in all fields');
      return;
    }
    setError('');
    setIsLoading(true);
    try {
      await login({ email: emailVal, password: passwordVal });
    } catch (err) {
      console.error('Login error:', err);
      setError(mapLoginError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    await runLogin(email, password);
  };

  const handleDemoSignIn = async () => {
    if (!hasDemoCredentials) return;
    setEmail(DEMO_EMAIL);
    setPassword(DEMO_PASSWORD);
    await runLogin(DEMO_EMAIL, DEMO_PASSWORD);
  };

  const copyToClipboard = async (text: string, field: 'email' | 'password') => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      toast.success(field === 'email' ? 'Email copied' : 'Password copied');
      setTimeout(() => setCopiedField(null), 2000);
    } catch {
      toast.error('Could not copy to clipboard');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-4">
      <Card className="w-full max-w-md border-slate-700/80 bg-slate-800/40 backdrop-blur-md shadow-2xl shadow-black/20">
        <CardHeader className="space-y-1 pb-2">
          <div className="flex items-center justify-center mb-3">
            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-900/40">
              <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          <CardTitle className="text-2xl text-center text-white tracking-tight">Welcome back</CardTitle>
          <CardDescription className="text-center text-slate-400">
            Sign in to your RunCoach AI account
          </CardDescription>
        </CardHeader>

        {hasDemoCredentials && (
          <div className="px-6 pb-2">
            <div
              className="relative overflow-hidden rounded-xl border border-amber-500/35 bg-gradient-to-b from-amber-950/50 to-slate-900/60 p-4 shadow-inner"
              role="region"
              aria-label="Demo account credentials"
            >
              <div className="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-amber-400/10 blur-2xl" />
              <div className="relative flex items-start gap-3">
                <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-500/15 text-amber-300 ring-1 ring-amber-500/25">
                  <Sparkles className="h-4 w-4" aria-hidden />
                </div>
                <div className="min-w-0 flex-1 space-y-3">
                  <div>
                    <p className="text-sm font-semibold text-amber-100/95">Try the demo</p>
                    <p className="mt-0.5 text-xs leading-relaxed text-slate-400">
                      Recruiters &amp; evaluators: use this account to explore the app with real sample data.
                    </p>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <p className="mb-1 text-[10px] font-medium uppercase tracking-wider text-slate-500">Email</p>
                      <div className="flex items-center gap-2 rounded-lg border border-slate-600/60 bg-slate-950/50 px-2.5 py-1.5">
                        <code className="min-w-0 flex-1 truncate text-xs text-slate-200">{DEMO_EMAIL}</code>
                        <button
                          type="button"
                          onClick={() => copyToClipboard(DEMO_EMAIL, 'email')}
                          className="inline-flex shrink-0 items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-amber-200/90 transition hover:bg-white/10"
                          aria-label="Copy demo email"
                        >
                          {copiedField === 'email' ? (
                            <Check className="h-3.5 w-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="h-3.5 w-3.5" />
                          )}
                          Copy
                        </button>
                      </div>
                    </div>
                    <div>
                      <p className="mb-1 text-[10px] font-medium uppercase tracking-wider text-slate-500">Password</p>
                      <div className="flex items-center gap-2 rounded-lg border border-slate-600/60 bg-slate-950/50 px-2.5 py-1.5">
                        <code className="min-w-0 flex-1 truncate text-xs text-slate-200">{DEMO_PASSWORD}</code>
                        <button
                          type="button"
                          onClick={() => copyToClipboard(DEMO_PASSWORD, 'password')}
                          className="inline-flex shrink-0 items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-amber-200/90 transition hover:bg-white/10"
                          aria-label="Copy demo password"
                        >
                          {copiedField === 'password' ? (
                            <Check className="h-3.5 w-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="h-3.5 w-3.5" />
                          )}
                          Copy
                        </button>
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleDemoSignIn}
                    disabled={isLoading}
                    className="w-full rounded-lg bg-gradient-to-r from-amber-500 to-amber-600 px-4 py-2.5 text-sm font-semibold text-slate-950 shadow-md shadow-amber-900/30 transition hover:from-amber-400 hover:to-amber-500 disabled:opacity-50 disabled:pointer-events-none"
                  >
                    {isLoading ? 'Signing in…' : 'Sign in with demo account'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <CardContent className="space-y-4 pt-2">
            {error && (
              <div className="rounded-lg border border-red-800/80 bg-red-950/40 p-3 text-sm text-red-300">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-200">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                className="border-slate-600 bg-slate-900/50 text-white placeholder:text-slate-500 focus-visible:ring-amber-500/40"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-200">
                Password
              </Label>
              <Input
                id="password"
                type="password"
                placeholder=""
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                className="border-slate-600 bg-slate-900/50 text-white placeholder:text-slate-500 focus-visible:ring-amber-500/40"
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full h-10 rounded-md bg-blue-600 px-4 py-2 font-medium text-white transition hover:bg-blue-500 disabled:opacity-50 disabled:pointer-events-none"
            >
              {isLoading ? 'Signing in…' : 'Sign in'}
            </button>
            <p className="text-center text-sm text-slate-400">
              Don&apos;t have an account?{' '}
              <Link href="/register" className="font-medium text-amber-400/90 hover:text-amber-300">
                Sign up
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
