-- Migration 011: Expand patient_documents doc_type CHECK constraint to support radiology
-- Preserves all 7 existing document types ('consultation', 'lab_report', 'procedure', 'ultrasound', 'discharge_summary', 'medication_record', 'pending_lab_order') and adds 'radiology'.

BEGIN;

ALTER TABLE public.patient_documents DROP CONSTRAINT IF EXISTS patient_documents_doc_type_check;
ALTER TABLE public.patient_documents ADD CONSTRAINT patient_documents_doc_type_check 
    CHECK (doc_type IN (
        'consultation', 'lab_report', 'procedure', 'ultrasound', 
        'discharge_summary', 'medication_record', 'pending_lab_order', 'radiology'
    ));

COMMIT;
