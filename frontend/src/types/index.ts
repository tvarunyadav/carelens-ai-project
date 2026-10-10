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
  record_version: number;
  user_grant?: 'read' | 'write' | 'admin';
  can_write?: boolean;
  created_at?: string;
}

export interface StaffProfile {
  id: string;
  email: string;
  full_name: string;
  role: 'doctor' | 'coordinator' | 'admin';
  created_at?: string;
}

export interface PatientListResponse {
  patients: Patient[];
  total: number;
}

export interface DocumentItem {
  id: string;
  patient_id: string;
  title: string;
  doc_type: string;
  clinical_date: string;
  status: 'final' | 'pending' | 'archived' | 'draft';
  storage_path?: string;
  mime_type: string;
  file_size: number;
  current_version: number;
}

export interface DocumentListResponse {
  documents: DocumentItem[];
  total: number;
}

export interface TimelineEventItem {
  id: string;
  patient_id: string;
  event_date: string;
  event_type: 'visit' | 'lab_result' | 'procedure' | 'medication' | 'fertility_cycle' | 'follow_up' | 'pending_order';
  title: string;
  summary: string;
  document_id?: string;
  metadata_json?: Record<string, any>;
}

export interface TimelineListResponse {
  events: TimelineEventItem[];
  total: number;
}

export interface FertilityCycleItem {
  id: string;
  patient_id: string;
  cycle_name: string;
  start_date: string;
  end_date?: string;
  status: 'active' | 'completed' | 'cancelled';
  notes_json?: Record<string, any>;
}

export interface FertilityCycleListResponse {
  cycles: FertilityCycleItem[];
  total: number;
}

export interface DocumentSourceResponse {
  document_id: string;
  title: string;
  download_url: string;
  expires_in_seconds: number;
  mime_type: string;
}

export interface Question {
  id: string;
  patient_id: string;
  text: string;
  asked_by: string;
  created_at: string;
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

export interface AIEvidenceItem {
  id: string;
  type: 'document_chunk' | 'fertility_cycle' | 'pending_order' | 'timeline_event';
  title: string;
  document_id?: string;
  document_version_id?: string;
  page_number?: number;
  date?: string;
  snippet: string;
}

export interface AIResponse {
  status: 'success' | 'ai_not_configured' | 'ai_model_unavailable' | 'ai_provider_unavailable' | 'error';
  answer: string;
  provider: string;
  evidence: AIEvidenceItem[];
  evidence_citations: string[];
  evidence_limitations?: string;
  detected_language?: 'en' | 'ta' | 'mixed';
  tamil_audio_text?: string;
}

