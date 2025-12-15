'use client';

/**
 * auth-context.tsx - Authentication context and provider
 */
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import type { User, LoginRequest, RegisterRequest } from '@/lib/types';

interface AuthContextType {
  user: User | null;
  userProfile: any | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  onboardingCompleted: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  refetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [onboardingCompleted, setOnboardingCompleted] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  // Check auth status on mount
  useEffect(() => {
    const token = apiClient.getToken();
    
    if (!token) {
      setIsLoading(false);
      return;
    }

    // Try to fetch onboarding status
    const checkOnboarding = async () => {
      try {
        const profile = await apiClient.getOnboardingStatus();
        if (profile) {
          setUserProfile(profile);
          setOnboardingCompleted(profile.onboarding_completed || false);
          
          // If on auth pages and authenticated, redirect based on onboarding status
          if (pathname === '/login' || pathname === '/register') {
            if (profile.onboarding_completed) {
              router.push('/dashboard');
            } else {
              router.push('/onboarding');
            }
          }
        }
      } catch (error) {
        console.error('Failed to fetch onboarding status:', error);
        // Don't fail silently - allow user to continue
        setOnboardingCompleted(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkOnboarding();
  }, [pathname, router]);

  // Protect onboarding route
  useEffect(() => {
    if (!isLoading && pathname === '/onboarding') {
      if (onboardingCompleted) {
        router.push('/dashboard');
      } else if (!apiClient.getToken()) {
        router.push('/login');
      }
    }
  }, [isLoading, onboardingCompleted, pathname, router]);

  // Protect dashboard and other authenticated routes
  useEffect(() => {
    if (!isLoading && pathname.startsWith('/dashboard')) {
      if (!apiClient.getToken()) {
        router.push('/login');
      } else if (!onboardingCompleted && userProfile) {
        router.push('/onboarding');
      }
    }
  }, [isLoading, onboardingCompleted, pathname, router, userProfile]);

  const login = async (credentials: LoginRequest) => {
    setIsLoading(true);
    try {
      const response = await apiClient.login(credentials);
      setUser(response.user);
      
      // Check onboarding status (pero no bloquear si falla)
      try {
        const profile = await apiClient.getOnboardingStatus();
        if (profile) {
          setUserProfile(profile);
          setOnboardingCompleted(profile.onboarding_completed || false);
          
          if (profile.onboarding_completed) {
            router.push('/dashboard');
          } else {
            router.push('/onboarding');
          }
        } else {
          // Profile es null/undefined, ir al dashboard de todas formas
          router.push('/dashboard');
        }
      } catch (error) {
        console.error('Failed to fetch profile after login:', error);
        // No dejes que esto bloquee - simplemente ve al dashboard
        router.push('/dashboard');
      }
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  const register = async (data: RegisterRequest) => {
    setIsLoading(true);
    try {
      const response = await apiClient.register(data);
      setUser(response.user);
      setOnboardingCompleted(false); // New users need onboarding
      router.push('/onboarding');
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  const logout = () => {
    apiClient.logout();
    setUser(null);
    setUserProfile(null);
    setOnboardingCompleted(false);
    router.push('/login');
  };

  const refetchUser = async () => {
    try {
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
      
      // Also refetch profile and onboarding status
      const profile = await apiClient.getOnboardingStatus();
      setUserProfile(profile);
      setOnboardingCompleted(profile.onboarding_completed || false);
    } catch (error) {
      console.error('Failed to refetch user:', error);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    userProfile,
    isLoading,
    isAuthenticated: !!user,
    onboardingCompleted,
    login,
    register,
    logout,
    refetchUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}
