import type {
  HealthStatus, APIError, StaffProfile, PatientListResponse, Patient,
  TimelineListResponse, DocumentListResponse, DocumentItem,
  DocumentSourceResponse, FertilityCycleListResponse, AIResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8010';
const DEFAULT_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS) || 12000;

export function formatApiErrorMessage(errData: any, defaultMsg: string): string {
  if (!errData) return defaultMsg;
  const raw = errData.detail ?? errData.message ?? errData.error;
  if (!raw) return defaultMsg;

  if (typeof raw === 'string') {
    const trimmed = raw.trim();
    if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
      try {
        const parsed = JSON.parse(trimmed);
        return parsed.message || parsed.detail || parsed.error || trimmed;
      } catch {}
    }
    return trimmed || defaultMsg;
  }

  if (Array.isArray(raw)) {
    const msgs = raw
      .map((item: any) => {
        if (typeof item === 'string') return item;
        if (item && typeof item === 'object') {
          const loc = Array.isArray(item.loc) ? item.loc.filter((l: any) => l !== 'body').join('.') : '';
          const msgStr = item.msg || item.message || '';
          return loc && msgStr ? `${loc}: ${msgStr}` : (msgStr || JSON.stringify(item));
        }
        return String(item);
      })
      .filter(Boolean);
    return msgs.length > 0 ? msgs.join('; ') : defaultMsg;
  }

  if (typeof raw === 'object') {
    return raw.message || raw.msg || raw.error || defaultMsg;
  }

  return String(raw);
}

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  public getBaseUrl(): string {
    return this.baseUrl;
  }

  private async fetchWithTimeout(
    endpoint: string,
    options: RequestInit = {},
    timeoutMs: number = DEFAULT_TIMEOUT_MS
  ): Promise<Response> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);

    const isFormData = options.body instanceof FormData;
    const reqHeaders: Record<string, string> = {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(options.headers as Record<string, string> || {}),
    };

    if (isFormData) {
      delete reqHeaders['Content-Type'];
      delete reqHeaders['content-type'];
    }

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: reqHeaders,
      });
      clearTimeout(id);
      return response;
    } catch (error: any) {
      clearTimeout(id);
      if (error.name === 'AbortError') {
        const err: APIError = {
          message: `Request timed out after ${timeoutMs}ms. Is the CareLens backend running at ${this.baseUrl}?`,
          isTimeout: true,
        };
        throw err;
      }
      const err: APIError = {
        message: error.message || `Network error occurred while connecting to CareLens backend at ${this.baseUrl}.`,
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

  async getPatientTimeline(patientId: string, accessToken: string, eventType?: string): Promise<TimelineListResponse> {
    const query = eventType ? `?event_type=${encodeURIComponent(eventType)}` : '';
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/timeline${query}`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `Failed to fetch patient timeline (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async getPatientDocuments(patientId: string, accessToken: string, docType?: string): Promise<DocumentListResponse> {
    const query = docType ? `?doc_type=${encodeURIComponent(docType)}` : '';
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/documents${query}`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `Failed to fetch patient documents (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async getPatientDocumentDetail(patientId: string, documentId: string, accessToken: string): Promise<DocumentItem> {
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/documents/${documentId}`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `Access denied or document not found (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async getPatientDocumentSourceUrl(patientId: string, documentId: string, accessToken: string): Promise<DocumentSourceResponse> {
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/documents/${documentId}/source-url`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `Access denied or document source unavailable (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async getPatientCycles(patientId: string, accessToken: string): Promise<FertilityCycleListResponse> {
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/cycles`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `Failed to fetch fertility cycles (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async downloadPatientDocumentBlob(patientId: string, documentId: string, accessToken: string, versionId?: string): Promise<Blob> {
    const endpoint = versionId
      ? `/api/v1/patients/${patientId}/documents/${documentId}/download?version_id=${versionId}`
      : `/api/v1/patients/${patientId}/documents/${documentId}/download`;

    const response = await this.fetchWithTimeout(endpoint, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `Access denied or document file unavailable (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('pdf') && !contentType.includes('image') && !contentType.includes('application/octet-stream') && !contentType.includes('binary')) {
      const text = await response.text();
      let msg = 'Invalid document format received from server.';
      try {
        const jsonErr = JSON.parse(text);
        if (jsonErr.detail) msg = jsonErr.detail;
      } catch {}
      const err: APIError = { message: msg, statusCode: response.status };
      throw err;
    }

    return response.blob();
  }

  async generatePatientAISummary(patientId: string, accessToken: string): Promise<AIResponse> {
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/ai/summary`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `Failed to generate AI history summary (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async queryPatientAI(
    patientId: string,
    query: string,
    accessToken: string,
    options?: { inputMode?: string }
  ): Promise<AIResponse> {
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/ai/query`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify({
        query,
        input_mode: options?.inputMode || 'typed',
      }),
    });


    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `AI query failed (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async transcribeSpeech(audioBlob: Blob, accessToken: string): Promise<{ status: string; transcript: string; detected_language: string }> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'speech.webm');

    const response = await this.fetchWithTimeout('/api/v1/speech/transcribe', {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
      body: formData,
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: errData.detail || `Speech transcription failed (${response.status})`,
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async uploadDocument(patientId: string, file: File, accessToken: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/documents/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
      body: formData,
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: formatApiErrorMessage(errData, `Document upload failed (${response.status})`),
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async uploadDocumentVersion(patientId: string, documentId: string, file: File, accessToken: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/documents/${documentId}/versions/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
      body: formData,
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: formatApiErrorMessage(errData, `Upload document version failed (${response.status})`),
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async reviewAndPublishDocument(patientId: string, documentId: string, reviewData: any, accessToken: string): Promise<any> {
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/documents/${documentId}/review`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify(reviewData),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: formatApiErrorMessage(errData, `Review and publish document failed (${response.status})`),
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async getDocumentVersions(patientId: string, documentId: string, accessToken: string): Promise<any[]> {
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/documents/${documentId}/versions`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: formatApiErrorMessage(errData, `Failed to fetch document versions (${response.status})`),
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async getActivityHistory(patientId: string, accessToken: string): Promise<any[]> {
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/activity-history`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: formatApiErrorMessage(errData, `Failed to fetch activity history (${response.status})`),
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async getConflictReviews(patientId: string, accessToken: string): Promise<any[]> {
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/conflict-reviews`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: formatApiErrorMessage(errData, `Failed to fetch conflict reviews (${response.status})`),
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }

  async createConflictReview(patientId: string, payload: any, accessToken: string): Promise<any> {
    const response = await this.fetchWithTimeout(`/api/v1/patients/${patientId}/conflict-reviews`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const err: APIError = {
        message: formatApiErrorMessage(errData, `Failed to record conflict review (${response.status})`),
        statusCode: response.status,
      };
      throw err;
    }

    return response.json();
  }
}



export const apiClient = new APIClient();
