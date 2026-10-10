import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import type { StaffProfile } from '../types';
import { apiClient } from '../services/api';
import { supabase } from '../lib/supabase';

interface AuthContextType {
  token: string | null;
  staff: StaffProfile | null;
  isLoading: boolean;
  error: string | null;
  loginWithSupabase: (email: string, pass: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('carelens_access_token'));
  const [staff, setStaff] = useState<StaffProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Ref to track the active token and avoid late responses overwriting session state
  const activeTokenRef = useRef<string | null>(token);
  activeTokenRef.current = token;

  // Ref to track active login in progress to prevent duplicate restoreSession calls
  const isLoggingInRef = useRef<boolean>(false);

  // Restore session on load or token change
  useEffect(() => {
    let isCancelled = false;

    async function restoreSession() {
      if (!token) {
        setStaff(null);
        setIsLoading(false);
        return;
      }

      // If manual login is currently in progress, skip duplicate restoration
      if (isLoggingInRef.current) {
        return;
      }

      // If staff profile is already loaded for this token, skip duplicate network call
      if (staff && localStorage.getItem('carelens_access_token') === token) {
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);
      try {
        const profile = await apiClient.getMe(token);
        if (!isCancelled && activeTokenRef.current === token) {
          setStaff(profile);
        }
      } catch (err: any) {
        if (!isCancelled && activeTokenRef.current === token) {
          setError(err.message || 'Session expired or invalid');
          setToken(null);
          setStaff(null);
          localStorage.removeItem('carelens_access_token');
        }
      } finally {
        if (!isCancelled && activeTokenRef.current === token) {
          setIsLoading(false);
        }
      }
    }

    restoreSession();

    return () => {
      isCancelled = true;
    };
  }, [token]);

  // Listen to real Supabase Auth state changes
  useEffect(() => {
    const { data: authListener } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.access_token) {
        if (session.access_token !== activeTokenRef.current) {
          setToken(session.access_token);
          localStorage.setItem('carelens_access_token', session.access_token);
        }
      } else if (event === 'SIGNED_OUT') {
        activeTokenRef.current = null;
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
    isLoggingInRef.current = true;
    setIsLoading(true);
    setError(null);

    const supabaseUrl = (import.meta.env.VITE_SUPABASE_URL || '').trim();
    const supabaseAnonKey = (import.meta.env.VITE_SUPABASE_ANON_KEY || '').trim();

    const isPlaceholderUrl = !supabaseUrl || supabaseUrl.includes('your-supabase-project') || supabaseUrl.includes('placeholder-project');
    const isPlaceholderKey = !supabaseAnonKey || supabaseAnonKey.includes('your-supabase-anon-key') || supabaseAnonKey.includes('placeholder-anon-key');

    if (isPlaceholderUrl || isPlaceholderKey) {
      const msg = 'Supabase credentials are not configured in frontend/.env. Please enter your real VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in frontend/.env.';
      setError(msg);
      setIsLoading(false);
      isLoggingInRef.current = false;
      throw new Error(msg);
    }

    try {
      // Clear previous session completely before logging in
      setStaff(null);
      setToken(null);
      localStorage.removeItem('carelens_access_token');
      await supabase.auth.signOut().catch(() => {});

      const { data, error: sbError } = await supabase.auth.signInWithPassword({
        email,
        password: pass,
      });

      if (sbError) {
        throw new Error(sbError.message);
      }

      if (data.session?.access_token) {
        const accessToken = data.session.access_token;
        activeTokenRef.current = accessToken;

        // Fetch verified profile BEFORE setting React token state to eliminate duplicate requests
        const profile = await apiClient.getMe(accessToken);
        
        localStorage.setItem('carelens_access_token', accessToken);
        setStaff(profile);
        setToken(accessToken);
      } else {
        throw new Error('No access token returned from Supabase Auth service');
      }
    } catch (err: any) {
      let msg = err.message || 'Login failed. Please check credentials.';
      if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
        msg = `Failed to connect to Supabase Auth at ${supabaseUrl}. Please verify your internet connection and VITE_SUPABASE_URL in frontend/.env.`;
      }
      setError(msg);
      setStaff(null);
      setToken(null);
      localStorage.removeItem('carelens_access_token');
      throw new Error(msg);
    } finally {
      isLoggingInRef.current = false;
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    activeTokenRef.current = null;
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
