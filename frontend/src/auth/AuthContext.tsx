import React, { createContext, useContext, useState, useEffect } from 'react';
import type { StaffProfile } from '../types';
import { apiClient } from '../services/api';
import { supabase } from '../lib/supabase';

interface AuthContextType {
  token: string | null;
  staff: StaffProfile | null;
  isLoading: boolean;
  error: string | null;
  loginWithSupabase: (email: string, pass: string) => Promise<void>;
  loginAsDevUser: (devUserKey: 'dev_user_alice' | 'dev_user_bob' | 'dev_user_admin') => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('carelens_access_token'));
  const [staff, setStaff] = useState<StaffProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Restore session on load or token change
  useEffect(() => {
    async function restoreSession() {
      if (!token) {
        setStaff(null);
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);
      try {
        const profile = await apiClient.getMe(token);
        setStaff(profile);
      } catch (err: any) {
        setError(err.message || 'Session expired or invalid');
        setToken(null);
        setStaff(null);
        localStorage.removeItem('carelens_access_token');
      } finally {
        setIsLoading(false);
      }
    }

    restoreSession();
  }, [token]);

  // Listen to real Supabase Auth state change if configured
  useEffect(() => {
    const { data: authListener } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.access_token) {
        setToken(session.access_token);
        localStorage.setItem('carelens_access_token', session.access_token);
      } else if (event === 'SIGNED_OUT') {
        setToken(null);
        setStaff(null);
        localStorage.removeItem('carelens_access_token');
      }
    });

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  const loginWithSupabase = async (email: string, pass: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const { data, error: sbError } = await supabase.auth.signInWithPassword({
        email,
        password: pass,
      });

      if (sbError) {
        throw new Error(sbError.message);
      }

      if (data.session?.access_token) {
        const accessToken = data.session.access_token;
        setToken(accessToken);
        localStorage.setItem('carelens_access_token', accessToken);
        const profile = await apiClient.getMe(accessToken);
        setStaff(profile);
      }
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check credentials.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const loginAsDevUser = async (devUserKey: 'dev_user_alice' | 'dev_user_bob' | 'dev_user_admin') => {
    setIsLoading(true);
    setError(null);
    try {
      const devToken = `test-token-${devUserKey}`;
      const profile = await apiClient.getMe(devToken);
      setToken(devToken);
      setStaff(profile);
      localStorage.setItem('carelens_access_token', devToken);
    } catch (err: any) {
      setError(err.message || 'Failed to login with test staff account');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await supabase.auth.signOut().catch(() => {});
    } finally {
      setToken(null);
      setStaff(null);
      setError(null);
      localStorage.removeItem('carelens_access_token');
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        staff,
        isLoading,
        error,
        loginWithSupabase,
        loginAsDevUser,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
