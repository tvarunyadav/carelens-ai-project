export interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

export interface Citation {
  id: string;
  document_id: string;
  document_name: string;
  page_number: number;
  text_snippet: string;
  bounding_box?: BoundingBox;
}

export interface Claim {
  id: string;
  text: string;
  confidence: number;
  citations: Citation[];
}

export interface Patient {
  id: string;
  mrn: string;
  first_name: string;
  last_name: string;
  dob: string;
  gender: string;
  status: 'active' | 'archived';
  created_at: string;
}

export interface Question {
  id: string;
  patient_id: string;
  text: string;
  asked_by: string;
  created_at: string;
}

export interface TimelineEvent {
  id: string;
  patient_id: string;
  event_date: string;
  category: 'Lab Result' | 'Diagnosis' | 'Medication' | 'Procedure' | 'Note';
  summary: string;
  document_id?: string;
}

export interface HealthStatus {
  status: 'ok' | 'degraded' | 'error';
  service: string;
  version: string;
  timestamp: string;
}

export interface APIError {
  message: string;
  statusCode?: number;
  isTimeout?: boolean;
}
