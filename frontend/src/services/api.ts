import type { HealthStatus, APIError, StaffProfile, PatientListResponse, Patient } from '../types';

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
          message: `Request timed out after ${timeoutMs}ms. Is the CareLens backend running?`,
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
    const response = await this.fetchWithTimeout('/health');
    if (!response.ok) {
      const err: APIError = {
        message: `Backend returned status ${response.status}: ${response.statusText}`,
        statusCode: response.status,
      };
      throw err;
    }
    return response.json();
  }

  async getMe(accessToken: string): Promise<StaffProfile> {
    const response = await this.fetchWithTimeout('/api/v1/me', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `Authentication failed (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async getPatients(accessToken: string): Promise<PatientListResponse> {
    const response = await this.fetchWithTimeout('/api/v1/patients', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `Failed to fetch patients (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async getPatientDetail(patientId: string, accessToken: string): Promise<Patient> {
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `Access denied or patient record not found (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }
}

export const apiClient = new APIClient();
