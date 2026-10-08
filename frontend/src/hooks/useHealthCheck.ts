import { useState, useCallback } from 'react';
import type { HealthStatus, APIError } from '../types';
import { apiClient } from '../services/api';

export interface HealthCheckState {
  status: 'idle' | 'loading' | 'success' | 'error';
  data: HealthStatus | null;
  error: APIError | null;
  lastCheckedAt: string | null;
}

export function useHealthCheck() {
  const [state, setState] = useState<HealthCheckState>({
    status: 'idle',
    data: null,
    error: null,
    lastCheckedAt: null,
  });

  const checkHealth = useCallback(async () => {
    setState({
      status: 'loading',
      data: null,
      error: null,
      lastCheckedAt: new Date().toLocaleTimeString(),
    });

    try {
      const data = await apiClient.checkHealth();
      setState({
        status: 'success',
        data,
        error: null,
        lastCheckedAt: new Date().toLocaleTimeString(),
      });
    } catch (err: any) {
      setState({
        status: 'error',
        data: null,
        error: err as APIError,
        lastCheckedAt: new Date().toLocaleTimeString(),
      });
    }
  }, []);

  return {
    ...state,
    checkHealth,
  };
}
