import type { HealthStatus, APIError } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT_MS = 5000;

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  private async fetchWithTimeout(
    endpoint: string,
    options: RequestInit = {},
    timeoutMs: number = DEFAULT_TIMEOUT_MS
  ): Promise<Response> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {}),
        },
      });
      clearTimeout(id);
      return response;
    } catch (error: any) {
      clearTimeout(id);
      if (error.name === 'AbortError') {
        const err: APIError = {
          message: `Request timed out after ${timeoutMs}ms. Is the backend running?`,
          isTimeout: true,
        };
        throw err;
      }
      const err: APIError = {
        message: error.message || 'Network error occurred while connecting to CareLens backend.',
      };
      throw err;
    }
  }

  async checkHealth(): Promise<HealthStatus> {
    try {
      const response = await this.fetchWithTimeout('/health');
      if (!response.ok) {
        const err: APIError = {
          message: `Backend returned status ${response.status}: ${response.statusText}`,
          statusCode: response.status,
        };
        throw err;
      }
      const data: HealthStatus = await response.json();
      return data;
    } catch (error) {
      throw error;
    }
  }
}

export const apiClient = new APIClient();
