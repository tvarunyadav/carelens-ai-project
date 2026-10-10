import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../auth/AuthContext';
import { apiClient } from '../services/api';
import type {
  Patient, TimelineEventItem, DocumentItem, FertilityCycleItem,
  AIResponse, AIEvidenceItem
} from '../types';
import { Card, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  ArrowLeft, Calendar, FileText, Activity, ShieldCheck, AlertCircle,
  Clock, Lock, RefreshCw, X, Eye, Download, Layers, CheckCircle2,
  Sparkles, MessageSquare, HelpCircle, Bot, Mic, MicOff, Volume2, VolumeX,
  Upload, FilePlus, GitBranch, CheckSquare
} from 'lucide-react';




interface PatientWorkspaceProps {
  patientId: string;
  onBack: () => void;
}

const getDocTypeLabel = (docType: string): string => {
  switch (docType) {
    case 'consultation': return 'Consultation Note';
    case 'lab_report': return 'Lab Report';
    case 'procedure': return 'Procedure Note';
    case 'ultrasound': return 'Ultrasound Report';
    case 'radiology': return 'Radiology Imaging';
    case 'medication_record': return 'Medication Order';
    case 'pending_lab_order': return 'Pending Order';
    default:
      return docType
        .split('_')
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' ');
  }
};

const SUGGESTED_QUESTIONS = [
  'What were her last two cycles, and which reports are pending?',
  'What were her last two cycles?',
  'Which reports are pending?',
  'What medications were recorded during the first cycle?',
];

export const PatientWorkspacePage: React.FC<PatientWorkspaceProps> = ({ patientId, onBack }) => {
  const { token } = useAuth();

  const [patient, setPatient] = useState<Patient | null>(null);
  const [timeline, setTimeline] = useState<TimelineEventItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [cycles, setCycles] = useState<FertilityCycleItem[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Derive write permission strictly from backend-confirmed patient grants (not staff role)
  const canWrite = Boolean(patient?.can_write ?? (patient?.user_grant === 'write' || patient?.user_grant === 'admin'));

  // Workspace Main Navigation Tabs
  const [activeTab, setActiveTab] = useState<'assistant' | 'timeline' | 'documents' | 'cycles' | 'history' | 'conflicts'>('assistant');
  const [selectedEventType, setSelectedEventType] = useState<string>('all');
  const [selectedDocType, setSelectedDocType] = useState<string>('all');
  const [activityHistory, setActivityHistory] = useState<any[]>([]);
  const [conflictReviews, setConflictReviews] = useState<any[]>([]);

  // History Assistant State
  const [userQuery, setUserQuery] = useState<string>('');
  const [aiLoading, setAiLoading] = useState<boolean>(false);
  const [aiResult, setAiResult] = useState<AIResponse | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

  // Document Source Viewer Modal State
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const [pdfBlobUrl, setPdfBlobUrl] = useState<string | null>(null);
  const [targetPage, setTargetPage] = useState<number>(1);
  const [pdfLoading, setPdfLoading] = useState<boolean>(false);
  const [pdfError, setPdfError] = useState<string | null>(null);

  const pdfBlobUrlRef = useRef<string | null>(null);
  pdfBlobUrlRef.current = pdfBlobUrl;

  const revokePdfUrl = () => {
    if (pdfBlobUrlRef.current) {
      URL.revokeObjectURL(pdfBlobUrlRef.current);
      pdfBlobUrlRef.current = null;
      setPdfBlobUrl(null);
    }
  };

  useEffect(() => {
    let isCancelled = false;

    // Reset workspace state on patientId or token change
    setPatient(null);
    setTimeline([]);
    setDocuments([]);
    setCycles([]);
    setError(null);
    setAiResult(null);
    setAiError(null);
    setUserQuery('');
    setSelectedDoc(null);
    revokePdfUrl();

    // Reset query, AI result, audio recording, and transcription on patient or token change
    stopAllAudioRecording();
    setUserQuery('');
    setAiResult(null);
    setIsVoiceUsed(false);
    setSpeechStatus('idle');
    setSpeechErrorMsg('');
    if (window.speechSynthesis) window.speechSynthesis.cancel();

    if (!token || !patientId) {
      setIsLoading(false);
      return;
    }

    async function loadWorkspaceData() {
      setIsLoading(true);
      setError(null);
      try {
        const [patData, timeData, docData, cycData, actData, confData] = await Promise.all([
          apiClient.getPatientDetail(patientId, token!),
          apiClient.getPatientTimeline(patientId, token!),
          apiClient.getPatientDocuments(patientId, token!),
          apiClient.getPatientCycles(patientId, token!),
          apiClient.getActivityHistory(patientId, token!).catch(() => []),
          apiClient.getConflictReviews(patientId, token!).catch(() => []),
        ]);

        if (!isCancelled) {
          setPatient(patData);
          setTimeline(timeData.events);
          setDocuments(docData.documents);
          setCycles(cycData.cycles);
          setActivityHistory(actData || []);
          setConflictReviews(confData || []);
        }
      } catch (err: any) {
        if (!isCancelled) {
          setError(err.message || 'Access denied or failed to load patient workspace.');
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }

    loadWorkspaceData();

    return () => {
      isCancelled = true;
      revokePdfUrl();
      stopAllAudioRecording();
    };
  }, [patientId, token]);


  const closeModal = () => {
    setSelectedDoc(null);
    setPdfError(null);
    setPdfLoading(false);
    setTargetPage(1);
    revokePdfUrl();
  };

  const handleOpenDocumentSource = async (doc: DocumentItem, initialPage: number = 1) => {
    if (!token) return;
    setSelectedDoc(doc);
    setTargetPage(initialPage);
    revokePdfUrl();
    setPdfError(null);

    if (doc.status === 'pending') {
      setPdfLoading(false);
      return;
    }

    setPdfLoading(true);
    try {
      const blob = await apiClient.downloadPatientDocumentBlob(patientId, doc.id, token);
      const url = URL.createObjectURL(blob);
      setPdfBlobUrl(url);
      refreshActivityHistoryWithDelay(600);
    } catch (err: any) {
      setPdfError(err.message || 'Failed to authorize and download original document.');
    } finally {
      setPdfLoading(false);
    }
  };

  // History Assistant & Multilingual Voice State (Milestone 5)
  const [isListening, setIsListening] = useState<boolean>(false);
  const [speechStatus, setSpeechStatus] = useState<'idle' | 'listening' | 'transcribing' | 'unsupported' | 'denied' | 'error'>('idle');
  const [speechErrorMsg, setSpeechErrorMsg] = useState<string>('');
  const [isVoiceUsed, setIsVoiceUsed] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [ttsNotice, setTtsNotice] = useState<string>('');

  // Milestone 6 Document Intake, Review & Versioning State
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadNotice, setUploadNotice] = useState<string>('');
  const [uploadError, setUploadError] = useState<string>('');
  const [duplicateNotice, setDuplicateNotice] = useState<string>('');
  const [activeReviewDoc, setActiveReviewDoc] = useState<any>(null);
  const [reviewTitle, setReviewTitle] = useState<string>('');
  const [reviewDocType, setReviewDocType] = useState<string>('consultation');
  const [reviewClinicalDate, setReviewClinicalDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [reviewExtractedText, setReviewExtractedText] = useState<string>('');
  const [reviewOrderId, setReviewOrderId] = useState<string>('');
  const [isAiSuggested, setIsAiSuggested] = useState<boolean>(false);
  const [isPublishing, setIsPublishing] = useState<boolean>(false);

  // Version History State
  const [versionHistoryDoc, setVersionHistoryDoc] = useState<DocumentItem | null>(null);
  const [versionList, setVersionList] = useState<any[]>([]);
  const [isLoadingVersions, setIsLoadingVersions] = useState<boolean>(false);
  const [selectedVersionForUpload, setSelectedVersionForUpload] = useState<DocumentItem | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const versionFileInputRef = useRef<HTMLInputElement | null>(null);

  const handleTriggerUpload = () => {
    setUploadNotice('');
    setUploadError('');
    setDuplicateNotice('');
    if (fileInputRef.current) fileInputRef.current.click();
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0 || !token) return;
    const file = files[0];
    e.target.value = '';

    setIsUploading(true);
    setUploadNotice('');
    setUploadError('');
    setDuplicateNotice('');

    try {
      const res = await apiClient.uploadDocument(patientId, file, token);
      if (res.status === 'duplicate_detected') {
        setDuplicateNotice(res.message);
      } else {
        setUploadNotice('File uploaded successfully! Please review metadata and published text.');
        setActiveReviewDoc(res);
        setReviewTitle(res.metadata_suggestions?.suggested_title || file.name);
        setReviewDocType(res.metadata_suggestions?.suggested_doc_type || 'consultation');
        setReviewClinicalDate(res.metadata_suggestions?.suggested_clinical_date || new Date().toISOString().split('T')[0]);
        setReviewExtractedText(res.extracted_text || '');
        setIsAiSuggested(Boolean(res.metadata_suggestions?.is_ai_suggestion));

        const docData = await apiClient.getPatientDocuments(patientId, token);
        setDocuments(docData.documents);
      }
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : (err?.message ? (typeof err.message === 'string' ? err.message : JSON.stringify(err.message)) : 'Access denied or unsupported file format.');
      setUploadError('Upload failed: ' + msg);
    } finally {
      setIsUploading(false);
    }
  };

  const handleTriggerVersionUpload = (doc: DocumentItem) => {
    setSelectedVersionForUpload(doc);
    setUploadNotice('');
    setUploadError('');
    setDuplicateNotice('');
    if (versionFileInputRef.current) versionFileInputRef.current.click();
  };

  const handleVersionFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0 || !token || !selectedVersionForUpload) return;
    const file = files[0];
    const targetDocId = selectedVersionForUpload.id;
    e.target.value = '';

    setIsUploading(true);
    setUploadNotice('');
    setUploadError('');
    setDuplicateNotice('');

    try {
      const res = await apiClient.uploadDocumentVersion(patientId, targetDocId, file, token);
      if (res.status === 'duplicate_version_detected') {
        setDuplicateNotice(res.message);
      } else {
        setUploadNotice(`Version v${res.version_number} uploaded successfully! Review and publish.`);
        setActiveReviewDoc(res);
        setReviewTitle(selectedVersionForUpload.title);
        setReviewDocType(selectedVersionForUpload.doc_type);
        setReviewClinicalDate(selectedVersionForUpload.clinical_date);
        setReviewExtractedText(res.extracted_text || '');
        setIsAiSuggested(false);

        const docData = await apiClient.getPatientDocuments(patientId, token);
        setDocuments(docData.documents);
      }
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : (err?.message ? (typeof err.message === 'string' ? err.message : JSON.stringify(err.message)) : 'Access denied or server error.');
      setUploadError('Version upload failed: ' + msg);
    } finally {
      setIsUploading(false);
      setSelectedVersionForUpload(null);
    }
  };

  const handleOpenReviewModal = (doc: DocumentItem) => {
    setActiveReviewDoc({
      document_id: doc.id,
      version_number: doc.current_version,
      extracted_text: ''
    });
    setReviewTitle(doc.title);
    setReviewDocType(doc.doc_type);
    setReviewClinicalDate(doc.clinical_date);
    setReviewExtractedText('');
    setReviewOrderId('');
    setIsAiSuggested(false);
  };

  const handleSaveAndPublishReview = async () => {
    if (!activeReviewDoc || !token) return;
    setIsPublishing(true);
    try {
      await apiClient.reviewAndPublishDocument(patientId, activeReviewDoc.document_id, {
        title: reviewTitle,
        doc_type: reviewDocType,
        clinical_date: reviewClinicalDate,
        extracted_text: reviewExtractedText,
        order_id: reviewOrderId || undefined
      }, token);

      setActiveReviewDoc(null);
      setUploadNotice('Document reviewed, published, and indexed for vector search!');

      const [docData, timeData] = await Promise.all([
        apiClient.getPatientDocuments(patientId, token),
        apiClient.getPatientTimeline(patientId, token)
      ]);
      setDocuments(docData.documents);
      setTimeline(timeData.events);
    } catch (err: any) {
      setUploadNotice('Failed to publish document: ' + (err.message || 'Access denied.'));
    } finally {
      setIsPublishing(false);
    }
  };

  const handleOpenVersionHistory = async (doc: DocumentItem) => {
    if (!token) return;
    setVersionHistoryDoc(doc);
    setIsLoadingVersions(true);
    setVersionList([]);
    try {
      const vers = await apiClient.getDocumentVersions(patientId, doc.id, token);
      setVersionList(vers);
    } catch (err: any) {
      setUploadNotice('Failed to load version history: ' + (err.message || 'Error loading versions'));
    } finally {
      setIsLoadingVersions(false);
    }
  };


  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<any>(null);

  const stopAllAudioRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try { mediaRecorderRef.current.stop(); } catch {}
    }
    if (mediaStreamRef.current) {
      try {
        mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      } catch {}
      mediaStreamRef.current = null;
    }
    if (recognitionRef.current) {
      try { recognitionRef.current.abort(); } catch {}
    }
    setIsListening(false);
  };

  // Resource cleanup on patient change or unmount
  useEffect(() => {
    return () => {
      stopAllAudioRecording();
      if (window.speechSynthesis) {
        try { window.speechSynthesis.cancel(); } catch {}
      }
    };
  }, [patientId]);

  const handleToggleSpeechInput = async () => {
    setSpeechErrorMsg('');
    if (isListening) {
      handleStopSpeech();
      return;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setSpeechStatus('unsupported');
      setSpeechErrorMsg('Microphone recording is not supported by this browser.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      audioChunksRef.current = [];

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        if (audioChunksRef.current.length === 0) {
          setSpeechStatus('idle');
          return;
        }
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        audioChunksRef.current = [];

        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach((t) => t.stop());
          mediaStreamRef.current = null;
        }

        if (!token) return;
        setSpeechStatus('transcribing');
        try {
          const res = await apiClient.transcribeSpeech(audioBlob, token);
          if (res.transcript && res.transcript.trim()) {
            setUserQuery(res.transcript);
            setIsVoiceUsed(true);
          }
          setSpeechStatus('idle');
        } catch (err: any) {
          setSpeechStatus('error');
          setSpeechErrorMsg(err.message || 'Speech transcription failed.');
        }
      };

      mediaRecorder.start();
      setIsListening(true);
      setSpeechStatus('listening');
      setIsVoiceUsed(true);
    } catch (err: any) {
      setIsListening(false);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setSpeechStatus('denied');
        setSpeechErrorMsg('Microphone access denied. Please allow microphone access in browser settings.');
      } else {
        setSpeechStatus('error');
        setSpeechErrorMsg('Unable to access microphone: ' + (err.message || String(err)));
      }
    }
  };

  const handleStopSpeech = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      try { mediaRecorderRef.current.stop(); } catch {}
      setIsListening(false);
    } else {
      stopAllAudioRecording();
      setSpeechStatus('idle');
    }
  };


  const handleClearSpeech = () => {
    handleStopSpeech();
    setUserQuery('');
    setIsVoiceUsed(false);
  };

  const handleReadAnswer = () => {
    setTtsNotice('');
    if (!window.speechSynthesis) {
      setTtsNotice('Speech Synthesis API unavailable in this browser.');
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    if (!aiResult || !aiResult.answer) return;

    const isTamilOrMixed = aiResult.detected_language === 'ta' || aiResult.detected_language === 'mixed';
    const textToRead = isTamilOrMixed && aiResult.tamil_audio_text
      ? aiResult.tamil_audio_text
      : aiResult.answer.replace(/\[EV-[A-Za-z0-9_\-]+\]/g, '').trim();

    if (!textToRead) return;

    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.lang = isTamilOrMixed ? 'ta-IN' : 'en-US';

    if (isTamilOrMixed) {
      const voices = window.speechSynthesis.getVoices();
      const taVoice = voices.find((v) => v.lang.includes('ta') || v.name.toLowerCase().includes('tamil'));
      if (!taVoice) {
        setTtsNotice('Tamil synthesis voice unavailable in this browser — English written answer remains fully readable.');
      } else {
        utterance.voice = taVoice;
      }
    }

    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  const refreshActivityHistoryWithDelay = (delayMs: number = 600) => {
    if (!token || !patientId) return;
    setTimeout(() => {
      apiClient.getActivityHistory(patientId, token)
        .then(hist => setActivityHistory(hist || []))
        .catch(() => {});
    }, delayMs);
  };

  const handleGenerateSummary = async () => {
    if (!token) return;
    setAiLoading(true);
    setAiError(null);
    try {
      const res = await apiClient.generatePatientAISummary(patientId, token);
      setAiResult(res);
      refreshActivityHistoryWithDelay(600);
    } catch (err: any) {
      setAiError(err.message || 'Failed to generate patient history summary.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleAskQuestion = async (queryText?: string) => {
    const q = (queryText || userQuery).trim();
    if (!token || !q) return;

    handleStopSpeech();
    if (window.speechSynthesis) {
      try { window.speechSynthesis.cancel(); } catch {}
    }
    setIsSpeaking(false);

    setUserQuery(q);
    setAiLoading(true);
    setAiError(null);
    try {
      const res = await apiClient.queryPatientAI(patientId, q, token, {
        inputMode: isVoiceUsed ? 'voice' : 'typed',
      });
      setAiResult(res);
      refreshActivityHistoryWithDelay(600);
    } catch (err: any) {
      setAiError(err.message || 'Failed to answer question.');
    } finally {
      setAiLoading(false);
    }
  };


  const handleEvidenceChipClick = (ev: AIEvidenceItem) => {
    if (ev.document_id) {
      const found = documents.find((d) => d.id === ev.document_id);
      if (found) {
        handleOpenDocumentSource(found, ev.page_number || 1);
        return;
      }
    }
    if (ev.type === 'fertility_cycle') {
      setActiveTab('cycles');
    } else if (ev.type === 'pending_order') {
      setActiveTab('documents');
      setSelectedDocType('pending_lab_order');
    } else {
      setActiveTab('timeline');
    }
  };

  const filteredTimeline = timeline.filter((e) => {
    if (selectedEventType === 'all') return true;
    return e.event_type === selectedEventType;
  });

  const filteredDocuments = documents.filter((d) => {
    if (selectedDocType === 'all') return true;
    return d.doc_type === selectedDocType;
  });

  const pendingLabOrders = documents.filter((d) => d.status === 'pending');

  const renderCycleMetrics = (notes?: Record<string, any>) => {
    if (!notes || Object.keys(notes).length === 0) return null;

    const oocytes = notes.oocytes_retrieved ?? notes.oocytes;
    const mature = notes.mature ?? notes.mature_oocytes;
    const blastocysts = notes.blastocysts_frozen ?? notes.blastocysts;
    const embryo = notes.embryo_transferred ?? notes.embryo;
    const outcome = notes.outcome ?? notes.recorded_outcome;

    const metrics = [
      { label: 'Oocytes retrieved', value: oocytes !== undefined ? String(oocytes) : null },
      { label: 'Mature oocytes', value: mature !== undefined ? String(mature) : null },
      { label: 'Blastocysts frozen', value: blastocysts !== undefined ? String(blastocysts) : null },
      { label: 'Embryo transferred', value: embryo !== undefined ? String(embryo) : null },
      { label: 'Recorded outcome', value: outcome !== undefined ? String(outcome) : null },
    ];

    return (
      <div className="bg-slate-950/90 p-3.5 rounded-xl border border-slate-800/80 space-y-2.5">
        <span className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
          Embryology & Cycle Metrics
        </span>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
          {metrics.map((m, idx) => {
            if (m.value === null) return null;
            return (
              <div key={idx} className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                <span className="block text-[10px] text-slate-400 font-medium">{m.label}</span>
                <span className="text-xs font-semibold text-teal-300 tracking-tight">{m.value}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="p-16 text-center text-slate-400 space-y-3">
        <RefreshCw className="w-8 h-8 text-teal-400 animate-spin mx-auto" />
        <p className="text-sm font-medium">Loading patient workspace & clinical records...</p>
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div className="space-y-4">
        <Button onClick={onBack} variant="outline" size="sm">
          <ArrowLeft className="w-4 h-4 mr-1.5" /> Back to Patient Directory
        </Button>

        <Card className="border-rose-900/60 bg-slate-950 p-8 text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-rose-950/80 border border-rose-800/80 flex items-center justify-center mx-auto text-rose-400">
            <Lock className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-lg font-bold text-rose-200">Access Restricted</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">{error || 'Patient record could not be loaded.'}</p>
          </div>
          <Button onClick={onBack} variant="primary" size="sm">
            Return to Directory
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <Button onClick={onBack} variant="outline" size="sm" className="w-fit">
          <ArrowLeft className="w-4 h-4 mr-1.5" /> Back to Patient Directory
        </Button>
      </div>

      {/* Patient Profile Header */}
      <Card className="border-teal-500/20 bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950">
        <div className="flex flex-col md:flex-row md:items-center justify-between p-5 gap-5">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2.5">
              <span className="text-xs font-mono font-bold text-teal-400 bg-teal-950 px-2 py-0.5 rounded border border-teal-800/60">
                {patient.mrn}
              </span>
              <Badge variant="success">Active File</Badge>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              {patient.first_name} {patient.last_name}
            </h2>
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
              <span><b>Gender:</b> {patient.gender}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-slate-500" />
                <b>DOB:</b> {patient.dob}
              </span>
              <span>•</span>
              <span><b>Record Revision:</b> v{patient.record_version}</span>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center gap-2.5">
            <div className="bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2 text-center min-w-[80px]">
              <span className="block text-base font-bold text-teal-400">{timeline.length}</span>
              <span className="text-[9px] text-slate-400 uppercase tracking-wider font-semibold">Events</span>
            </div>
            <div className="bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2 text-center min-w-[80px]">
              <span className="block text-base font-bold text-cyan-400">{documents.length}</span>
              <span className="text-[9px] text-slate-400 uppercase tracking-wider font-semibold">Documents</span>
            </div>
            {cycles.length > 0 && (
              <div className="bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2 text-center min-w-[80px]">
                <span className="block text-base font-bold text-emerald-400">{cycles.length}</span>
                <span className="text-[9px] text-slate-400 uppercase tracking-wider font-semibold">Cycles</span>
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Outstanding / Pending Lab Orders Alert Box */}
      {pendingLabOrders.length > 0 ? (
        <div className="bg-amber-950/40 border border-amber-800/60 rounded-xl p-3.5 text-amber-200 text-xs space-y-2">
          <div className="flex items-center gap-2 font-bold text-amber-300">
            <Clock className="w-4 h-4 text-amber-400 flex-shrink-0" />
            Outstanding / Pending Lab Orders ({pendingLabOrders.length})
          </div>
          <div className="space-y-1.5 pl-6">
            {pendingLabOrders.map((pDoc) => (
              <div key={pDoc.id} className="flex items-center justify-between border-b border-amber-900/40 pb-1.5 last:border-0">
                <span><b>{pDoc.title}</b> — Requested: {pDoc.clinical_date}</span>
                <span className="text-[11px] bg-amber-900/80 text-amber-300 px-2 py-0.5 rounded font-mono font-medium">
                  Result not yet recorded
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3 text-xs text-slate-400 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-teal-400 flex-shrink-0" />
          <span>No pending orders or incomplete lab results for this patient file.</span>
        </div>
      )}

      {/* Workspace Main Navigation Tabs */}
      <div className="border-b border-slate-800 flex items-center gap-2 pb-1">
        <button
          onClick={() => setActiveTab('assistant')}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
            activeTab === 'assistant'
              ? 'bg-teal-500 text-slate-950 shadow'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-300" />
          History Assistant
        </button>
        <button
          onClick={() => setActiveTab('timeline')}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
            activeTab === 'timeline'
              ? 'bg-teal-500 text-slate-950 shadow'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          Clinical Timeline ({timeline.length})
        </button>
        <button
          onClick={() => setActiveTab('documents')}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
            activeTab === 'documents'
              ? 'bg-teal-500 text-slate-950 shadow'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          Recorded Documents ({documents.length})
        </button>
        {cycles.length > 0 && (
          <button
            onClick={() => setActiveTab('cycles')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
              activeTab === 'cycles'
                ? 'bg-teal-500 text-slate-950 shadow'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Fertility Cycles ({cycles.length})
          </button>
        )}
        <button
          onClick={() => setActiveTab('history')}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
            activeTab === 'history'
              ? 'bg-teal-500 text-slate-950 shadow'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <Clock className="w-3.5 h-3.5 text-sky-400" />
          Activity History ({activityHistory.length})
        </button>
        <button
          onClick={() => setActiveTab('conflicts')}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
            activeTab === 'conflicts'
              ? 'bg-amber-500 text-slate-950 shadow'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
          Conflict Reviews ({conflictReviews.length})
        </button>
      </div>

      {/* TAB 0: HISTORY ASSISTANT (RAG) */}
      {activeTab === 'assistant' && (
        <div className="space-y-4">
          <Card className="border-teal-500/30 bg-slate-900/90 p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div className="space-y-1">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Bot className="w-4 h-4 text-teal-400" /> Patient History Assistant
                </h3>
                <p className="text-xs text-slate-400">
                  Ask about this patient’s history and check the original sources.
                </p>
              </div>

              <Button
                onClick={handleGenerateSummary}
                disabled={aiLoading}
                variant="primary"
                size="sm"
                className="w-fit"
              >
                {aiLoading ? <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 mr-1.5" />}
                Generate History Summary
              </Button>
            </div>

            {/* Suggested Questions */}
            <div className="space-y-2">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                <HelpCircle className="w-3.5 h-3.5 text-teal-400" /> Suggested Questions:
              </span>
              <div className="flex flex-wrap items-center gap-2">
                {SUGGESTED_QUESTIONS.map((sq, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleAskQuestion(sq)}
                    disabled={aiLoading}
                    className="text-xs text-slate-300 bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-teal-500/40 px-3 py-1 rounded-lg transition-colors text-left"
                  >
                    {sq}
                  </button>
                ))}
              </div>
            </div>

            {/* Listening / Speech Status Banner */}
            {isListening && (
              <div className="p-3 bg-teal-950/40 border border-teal-500/50 rounded-xl text-teal-200 text-xs flex items-center justify-between animate-pulse">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
                  <span className="font-semibold">
                    Listening ({speechStatus})... Speak in Tamil, English, or mixed Tamil-English.
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Button onClick={handleStopSpeech} variant="outline" size="sm" className="h-7 text-[11px] px-2">
                    Stop Listening
                  </Button>
                  <Button onClick={handleClearSpeech} variant="ghost" size="sm" className="h-7 text-[11px] px-2 text-rose-300 hover:bg-rose-950">
                    Clear
                  </Button>
                </div>
              </div>
            )}

            {/* Speech Notice / Error Banner */}
            {speechErrorMsg && (
              <div className="p-3 bg-amber-950/40 border border-amber-800/60 rounded-xl text-amber-200 text-xs flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                  <span>{speechErrorMsg}</span>
                </div>
                <button
                  onClick={() => setSpeechErrorMsg('')}
                  className="text-amber-400 hover:text-white text-xs px-2"
                >
                  Dismiss
                </button>
              </div>
            )}

            {/* Privacy & Speech Processing Disclaimer */}
            <div className="text-[10px] text-slate-500 flex items-center gap-1.5 px-1">
              <span>Audio is sent to an external AI transcription provider for processing; CareLens does not retain audio recordings.</span>
            </div>


            {/* Plain-Language Question & Voice Input Controls */}
            <div className="flex items-center gap-2 pt-1">
              <Button
                onClick={handleToggleSpeechInput}
                disabled={aiLoading}
                variant="outline"
                size="sm"
                title={isListening ? 'Stop listening' : 'Start voice recognition (English/Tamil)'}
                className={`border-teal-500/40 text-teal-300 ${
                  isListening ? 'bg-rose-600 text-white border-rose-500 hover:bg-rose-700' : 'hover:bg-teal-950/40'
                }`}
              >
                {isListening ? <MicOff className="w-4 h-4 animate-bounce" /> : <Mic className="w-4 h-4 text-teal-400" />}
              </Button>

              <input
                type="text"
                placeholder="Ask a question or click microphone to speak (Tamil or English)..."
                value={userQuery}
                onChange={(e) => {
                  setUserQuery(e.target.value);
                  if (isVoiceUsed) setIsVoiceUsed(false); // mark edited
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleAskQuestion();
                }}
                disabled={aiLoading}
                className="flex-1 bg-slate-950 border border-slate-800 focus:border-teal-500 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 outline-none transition-colors font-sans"
              />

              {userQuery.trim() && (
                <Button
                  onClick={handleClearSpeech}
                  variant="ghost"
                  size="sm"
                  title="Clear input"
                  className="text-slate-400 hover:text-white px-2"
                >
                  <X className="w-4 h-4" />
                </Button>
              )}

              <Button
                onClick={() => handleAskQuestion()}
                disabled={aiLoading || !userQuery.trim()}
                variant="outline"
                size="sm"
                className="border-teal-500/40 text-teal-300 hover:bg-teal-950/40"
              >
                {aiLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <MessageSquare className="w-3.5 h-3.5 mr-1" />}
                Ask
              </Button>
            </div>
          </Card>

          {/* AI Result / Response Container */}
          {aiLoading && (
            <div className="p-12 text-center text-slate-400 space-y-3 bg-slate-900/60 rounded-xl border border-slate-800">
              <RefreshCw className="w-7 h-7 text-teal-400 animate-spin mx-auto" />
              <p className="text-xs font-medium">Retrieving authorized clinical context & generating grounded response...</p>
            </div>
          )}

          {aiError && (
            <div className="p-5 bg-rose-950/60 border border-rose-800 rounded-xl text-rose-300 text-xs space-y-2">
              <div className="flex items-center gap-2 font-bold text-rose-200">
                <AlertCircle className="w-4 h-4 text-rose-400" /> AI Retrieval Error
              </div>
              <p>{aiError}</p>
            </div>
          )}

          {aiResult && !aiLoading && (
            <Card className="border-teal-500/40 bg-slate-900/90 p-5 space-y-4">
              {/* Header Badge & Audio Readout Toggle */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-teal-300">
                    {aiResult.status === 'success' ? 'AI Grounded Answer' : 'Recorded Patient Records'}
                  </span>
                  {aiResult.detected_language && aiResult.detected_language !== 'en' && (
                    <Badge variant="info" className="text-[10px] text-teal-300 border-teal-500/50">
                      Query: {aiResult.detected_language.toUpperCase()}
                    </Badge>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    onClick={handleReadAnswer}
                    variant="outline"
                    size="sm"
                    className={`h-7 text-xs border-teal-500/40 text-teal-300 ${
                      isSpeaking ? 'bg-teal-950 border-teal-400 text-teal-200' : 'hover:bg-teal-950/40'
                    }`}
                  >
                    {isSpeaking ? (
                      <>
                        <VolumeX className="w-3.5 h-3.5 mr-1 text-rose-400 animate-pulse" /> Stop Readout
                      </>
                    ) : (
                      <>
                        <Volume2 className="w-3.5 h-3.5 mr-1 text-teal-400" /> Read Answer
                      </>
                    )}
                  </Button>

                  {aiResult.status === 'success' ? (
                    <Badge variant="success">AI-generated</Badge>
                  ) : (
                    <Badge variant="warning">Recorded facts — AI temporarily unavailable</Badge>
                  )}
                </div>
              </div>

              {/* TTS Notice if Tamil TTS voice is unavailable */}
              {ttsNotice && (
                <div className="p-2.5 bg-amber-950/40 border border-amber-800/60 rounded-lg text-amber-200 text-xs flex items-center justify-between">
                  <span>{ttsNotice}</span>
                  <button onClick={() => setTtsNotice('')} className="text-amber-400 text-[11px] ml-2">
                    Dismiss
                  </button>
                </div>
              )}

              {/* Answer Content */}
              <div className="text-xs text-slate-200 leading-relaxed whitespace-pre-wrap font-sans">
                {aiResult.answer}
              </div>

              {/* Evidence Limitations Notice */}
              {aiResult.evidence_limitations && (
                <div className="p-3 bg-amber-950/30 border border-amber-800/40 rounded-lg text-amber-300 text-[11px] space-y-1">
                  <b>Evidence Notice:</b> {aiResult.evidence_limitations}
                </div>
              )}

              {/* Supporting Evidence Chips (ONLY items cited in aiResult.evidence_citations) */}
              {(() => {
                const citedItems = (aiResult.evidence || []).filter((ev) =>
                  (aiResult.evidence_citations || []).includes(ev.id)
                );
                if (citedItems.length === 0) return null;
                return (
                  <div className="pt-2 border-t border-slate-800 space-y-2">
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                      Supporting Clinical Evidence ({citedItems.length} items):
                    </span>
                    <div className="flex flex-wrap items-center gap-2">
                      {citedItems.map((ev) => (
                        <button
                          key={ev.id}
                          onClick={() => handleEvidenceChipClick(ev)}
                          className="text-xs px-2.5 py-1 rounded-lg border transition-all text-left flex items-center gap-1.5 bg-teal-950/80 text-teal-200 border-teal-500/60 hover:bg-teal-900"
                        >
                          <FileText className="w-3 h-3 text-teal-400 flex-shrink-0" />
                          <span className="font-semibold font-mono text-[10px]">[{ev.id}]</span>
                          <span>{ev.title}</span>
                          {ev.page_number && <span className="text-[10px] text-teal-400 font-mono">P.{ev.page_number}</span>}
                          {ev.date && <span className="text-[10px] text-slate-500">({ev.date})</span>}
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })()}


              {/* Medical Disclaimer Banner */}
              <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-500 italic">
                Notice: CareLens AI describes historical records only and provides no medical advice or diagnostic recommendations.
              </div>

              {/* Developer Diagnostics (Hidden from Ordinary Staff UI) */}
              <details className="pt-2 border-t border-slate-800/60 text-[10px] text-slate-500">
                <summary className="cursor-pointer hover:text-slate-400 font-mono">
                  Developer Details (System Diagnostics)
                </summary>
                <div className="mt-1.5 p-2 bg-slate-950 rounded font-mono text-[10px] text-slate-400 space-y-1 border border-slate-800">
                  <div>Provider: {aiResult.provider}</div>
                  <div>Status Code: {aiResult.status}</div>
                  {aiResult.evidence_limitations && <div>Limitations: {aiResult.evidence_limitations}</div>}
                </div>
              </details>
            </Card>
          )}
        </div>
      )}

      {/* TAB 1: CHRONOLOGICAL TIMELINE */}
      {activeTab === 'timeline' && (
        <div className="space-y-3.5">
          {/* Event Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5 bg-slate-900/60 p-2 rounded-xl border border-slate-800 text-xs">
            <span className="text-slate-400 font-medium px-1.5">Filter Category:</span>
            {[
              { id: 'all', label: 'All Events' },
              { id: 'visit', label: 'Visits' },
              { id: 'lab_result', label: 'Labs' },
              { id: 'procedure', label: 'Procedures' },
              { id: 'medication', label: 'Medications' },
              { id: 'follow_up', label: 'Follow-ups' },
              { id: 'pending_order', label: 'Pending Orders' },
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setSelectedEventType(f.id)}
                className={`px-2 py-0.5 rounded-md transition-colors font-medium text-[11px] ${
                  selectedEventType === f.id
                    ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {filteredTimeline.length === 0 ? (
            <div className="p-10 text-center text-slate-500 text-xs">
              No matching clinical timeline events found for the selected filter.
            </div>
          ) : (
            <div className="relative pl-5 border-l-2 border-slate-800 space-y-4">
              {filteredTimeline.map((ev) => {
                const linkedDoc = documents.find((d) => d.id === ev.document_id);
                return (
                  <div key={ev.id} className="relative group">
                    <div className="absolute -left-[27px] top-2 w-3 h-3 rounded-full bg-slate-950 border-2 border-teal-400 group-hover:border-teal-300 transition-colors" />

                    <div className="bg-slate-900/90 hover:bg-slate-900 border border-slate-800 hover:border-teal-500/40 rounded-xl p-3.5 transition-all duration-200 space-y-2">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 border-b border-slate-800/80 pb-1.5">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-slate-200">{ev.title}</span>
                          <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-950 text-teal-400 border border-slate-800">
                            {ev.event_type.replace('_', ' ')}
                          </span>
                        </div>
                        <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                          <Calendar className="w-3 h-3 text-slate-500" />
                          {ev.event_date}
                        </span>
                      </div>

                      <p className="text-xs text-slate-300 leading-normal">{ev.summary}</p>

                      {linkedDoc && (
                        <div className="pt-1.5 flex items-center justify-end">
                          <Button
                            onClick={() => handleOpenDocumentSource(linkedDoc)}
                            variant="outline"
                            size="sm"
                            className="text-xs text-teal-400 hover:text-teal-300 border-teal-500/30 hover:bg-teal-950/40 h-7 px-2.5"
                          >
                            <FileText className="w-3 h-3 mr-1" />
                            {linkedDoc.status === 'pending' ? 'View Pending Order Details' : 'Original document'}
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: RECORDED DOCUMENTS */}
      {activeTab === 'documents' && (
        <div className="space-y-3.5">
          {/* Hidden File Inputs for Document & Version Uploads */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
            className="hidden"
          />
          <input
            type="file"
            ref={versionFileInputRef}
            onChange={handleVersionFileUpload}
            accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
            className="hidden"
          />

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800 text-xs">
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-slate-400 font-medium px-1.5">Filter Type:</span>
              {[
                { id: 'all', label: 'All Documents' },
                { id: 'consultation', label: 'Consultations' },
                { id: 'lab_report', label: 'Lab Reports' },
                { id: 'procedure', label: 'Procedures' },
                { id: 'ultrasound', label: 'Ultrasound' },
                { id: 'medication_record', label: 'Medication Orders' },
                { id: 'pending_lab_order', label: 'Pending Orders' },
              ].map((f) => (
                <button
                  key={f.id}
                  onClick={() => setSelectedDocType(f.id)}
                  className={`px-2 py-0.5 rounded-md transition-colors font-medium text-[11px] ${
                    selectedDocType === f.id
                      ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {canWrite && (
              <Button
                onClick={handleTriggerUpload}
                disabled={isUploading}
                variant="primary"
                size="sm"
                className="h-8 text-xs font-semibold px-3 w-fit"
              >
                {isUploading ? <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Upload className="w-3.5 h-3.5 mr-1.5" />}
                Upload Document
              </Button>
            )}
          </div>

          {/* Upload Success Notice */}
          {uploadNotice && (
            <div className="p-3 bg-teal-950/40 border border-teal-500/50 rounded-xl text-teal-200 text-xs flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-teal-400 flex-shrink-0" />
                <span>{uploadNotice}</span>
              </div>
              <button onClick={() => setUploadNotice('')} className="text-teal-400 hover:text-white text-xs px-2">Dismiss</button>
            </div>
          )}

          {/* Upload Error Notice */}
          {uploadError && (
            <div className="p-3 bg-rose-950/40 border border-rose-500/50 rounded-xl text-rose-200 text-xs flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                <span className="font-semibold">{uploadError}</span>
              </div>
              <button onClick={() => setUploadError('')} className="text-rose-400 hover:text-white text-xs px-2">Dismiss</button>
            </div>
          )}

          {/* Duplicate Content Hash Notice */}
          {duplicateNotice && (
            <div className="p-3 bg-amber-950/40 border border-amber-800/60 rounded-xl text-amber-200 text-xs flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                <span className="font-semibold">{duplicateNotice}</span>
              </div>
              <button onClick={() => setDuplicateNotice('')} className="text-amber-400 hover:text-white text-xs px-2">Dismiss</button>
            </div>
          )}

          {filteredDocuments.length === 0 ? (
            <div className="p-10 text-center text-slate-500 text-xs">
              No clinical documents match the selected document filter.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {filteredDocuments.map((doc) => (
                <div
                  key={doc.id}
                  className="bg-slate-900/90 border border-slate-800 hover:border-teal-500/50 rounded-xl p-3.5 flex flex-col justify-between gap-3 transition-all duration-200"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono font-medium bg-slate-950 text-teal-300 px-2 py-0.5 rounded border border-slate-800">
                        {getDocTypeLabel(doc.doc_type)}
                      </span>
                      <div className="flex items-center gap-1.5">
                        {doc.status === 'draft' ? (
                          <Badge variant="warning">Review Pending</Badge>
                        ) : doc.status === 'pending' ? (
                          <Badge variant="warning">Result Not Recorded</Badge>
                        ) : (
                          <Badge variant="success">Final Reviewed</Badge>
                        )}
                      </div>
                    </div>

                    <h4 className="text-xs font-bold text-slate-100">{doc.title}</h4>
                    <div className="text-[11px] text-slate-400 flex items-center gap-2.5">
                      <span>Clinical Date: <b>{doc.clinical_date}</b></span>
                      <span>•</span>
                      <span>Version: <b>v{doc.current_version}</b></span>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5">
                      {canWrite && (
                        <Button
                          onClick={() => handleTriggerVersionUpload(doc)}
                          variant="ghost"
                          size="sm"
                          title="Upload new version N+1"
                          className="text-[11px] text-slate-300 hover:text-white h-7 px-2 hover:bg-slate-800"
                        >
                          <FilePlus className="w-3 h-3 mr-1 text-teal-400" /> New Ver
                        </Button>
                      )}
                      <Button
                        onClick={() => handleOpenVersionHistory(doc)}
                        variant="ghost"
                        size="sm"
                        title="View version history & diff"
                        className="text-[11px] text-slate-300 hover:text-white h-7 px-2 hover:bg-slate-800"
                      >
                        <GitBranch className="w-3.5 h-3.5 mr-1 text-amber-400" /> History
                      </Button>
                    </div>

                    <div className="flex items-center gap-1.5">
                      {doc.status === 'draft' && canWrite && (
                        <Button
                          onClick={() => handleOpenReviewModal(doc)}
                          variant="outline"
                          size="sm"
                          className="text-[11px] text-amber-300 border-amber-500/40 hover:bg-amber-950/40 h-7 px-2"
                        >
                          <CheckSquare className="w-3 h-3 mr-1 text-amber-400" /> Review & Publish
                        </Button>
                      )}
                      <Button
                        onClick={() => handleOpenDocumentSource(doc)}
                        variant="outline"
                        size="sm"
                        className="text-xs text-teal-400 hover:text-teal-300 h-7 px-2.5"
                      >
                        <Eye className="w-3.5 h-3.5 mr-1" />
                        {doc.status === 'pending' ? 'View Order Note' : 'Original file'}
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: FERTILITY CYCLES */}
      {activeTab === 'cycles' && (
        <div className="space-y-3.5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {cycles.map((cyc) => (
              <div key={cyc.id} className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <h4 className="text-xs font-bold text-teal-300">{cyc.cycle_name}</h4>
                  <Badge variant="success">{cyc.status}</Badge>
                </div>

                <div className="text-xs text-slate-400 space-y-0.5">
                  <div><b>Start Date:</b> {cyc.start_date}</div>
                  {cyc.end_date && <div><b>End Date:</b> {cyc.end_date}</div>}
                </div>

                {renderCycleMetrics(cyc.notes_json)}
              </div>
            ))}
          </div>
        </div>
      )}
      {/* TAB 4: ACTIVITY HISTORY */}
      {activeTab === 'history' && (
        <div className="space-y-3.5">
          <Card className="border-slate-800 bg-slate-900/90 p-4 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-xs font-bold text-teal-300 flex items-center gap-2">
                <Clock className="w-4 h-4 text-sky-400" /> Patient Audit & Activity History
              </h3>
              <Badge variant="neutral" className="text-[10px] text-slate-400">
                {activityHistory.length} Recorded Events
              </Badge>
            </div>
            {activityHistory.length === 0 ? (
              <div className="text-center py-6 text-xs text-slate-400">
                No recorded audit events for this patient file yet.
              </div>
            ) : (
              <div className="space-y-2.5 max-h-[600px] overflow-y-auto pr-1">
                {activityHistory.map((evt, idx) => (
                  <div key={evt.id || idx} className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge className="bg-sky-950 text-sky-300 border-sky-800 text-[10px] font-mono">
                          {evt.action || 'system_event'}
                        </Badge>
                        <span className="text-slate-300 font-medium">{evt.resource || 'patient_record'}</span>
                      </div>
                      <span className="text-[10px] text-slate-500">{evt.created_at ? new Date(evt.created_at).toLocaleString() : ''}</span>
                    </div>
                    <div className="text-[11px] text-slate-400 flex flex-wrap items-center gap-x-2 gap-y-1">
                      <span>Staff ID: <strong className="text-slate-300 font-mono">{evt.staff_id || 'system'}</strong></span>
                      {evt.details_json && Object.keys(evt.details_json).length > 0 && (
                        <span className="text-slate-300">
                          • {Object.entries(evt.details_json).map(([k, v]) => `${k.replace(/_/g, ' ')}: ${typeof v === 'object' ? JSON.stringify(v) : v}`).join(' | ')}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      )}

      {/* TAB 5: CLINICAL CONFLICT REVIEWS & CROSS-DOCUMENT RECONCILIATION */}
      {activeTab === 'conflicts' && (
        <div className="space-y-3.5">
          <Card className="border-amber-500/30 bg-slate-900/90 p-4 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-xs font-bold text-amber-300 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-amber-400" /> Cross-Document Comparisons & Conflict Reviews
              </h3>
              <Badge variant="warning" className="text-[10px]">
                {conflictReviews.length} Persisted Reviews
              </Badge>
            </div>
            <p className="text-xs text-slate-400">
              Cross-document clinical reconciliation analyzes extracted numerical metrics (e.g. lab values, hormone panels, follicle counts) across visits. Values recorded on separate dates reflect expected temporal progression (trend analysis), whereas identical clinical context discrepancies trigger human conflict review. The document list below displays confirmed reviewed source evidence.
            </p>

            {/* Dynamic Patient Document Evidence Stream */}
            <div className="space-y-2 bg-slate-950/80 p-3 rounded-xl border border-slate-800">
              <h4 className="text-xs font-semibold text-teal-300 flex items-center gap-2">
                <FileText className="w-3.5 h-3.5" /> Reviewed Source Documents Stream ({documents.filter(d => d.status === 'final').length} Confirmed Reviewed Records)
              </h4>
              {documents.filter(d => d.status === 'final').length === 0 ? (
                <p className="text-xs text-slate-500 italic py-2">No reviewed document records available for cross-document comparison.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 pt-1">
                  {documents.filter(d => d.status === 'final').map((doc) => (
                    <div key={doc.id} className="bg-slate-900/90 border border-slate-800 rounded-lg p-3 space-y-2 text-xs">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <span className="font-bold text-slate-200 block">{doc.title}</span>
                          <span className="text-[10px] text-teal-400 font-mono">Date: {doc.clinical_date} &bull; v{doc.current_version} &bull; {getDocTypeLabel(doc.doc_type)}</span>
                        </div>
                        <Badge variant="success" className="text-[9px] font-mono">
                          {doc.status}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between border-t border-slate-800/80 pt-2">
                        <span className="text-[10px] text-slate-500 font-mono">Source ID: {doc.id.slice(0, 8)}...</span>
                        <Button
                          onClick={() => handleOpenDocumentSource(doc)}
                          variant="outline"
                          size="sm"
                          className="text-[11px] text-teal-400 hover:text-teal-300 h-6 px-2"
                        >
                          <Eye className="w-3 h-3 mr-1" /> Original file
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Persisted Clinical Conflict Reviews */}
            {conflictReviews.length === 0 ? (
              <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl text-center space-y-2 text-xs text-slate-400">
                <CheckCircle2 className="w-6 h-6 text-teal-400 mx-auto" />
                <p className="font-medium text-slate-300">No unresolved clinical value contradictions detected.</p>
                <p className="text-[11px] text-slate-500 max-w-md mx-auto">
                  All recorded clinical lab metrics and consultation notes across different dates demonstrate expected temporal progression.
                </p>
              </div>
            ) : (
              <div className="space-y-3 pt-2">
                <h4 className="text-xs font-semibold text-amber-300">Recorded Discrepancy Resolutions</h4>
                {conflictReviews.map((rev, idx) => (
                  <div key={rev.id || idx} className="p-3 bg-slate-950/90 border border-amber-500/30 rounded-xl space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-amber-300">{rev.field_name || 'Clinical Metric'}</span>
                      <Badge className={rev.review_status?.includes('resolved') ? 'bg-teal-950 text-teal-300 border-teal-800' : 'bg-amber-950 text-amber-300 border-amber-800'}>
                        {rev.review_status}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-2 p-2 bg-slate-900/60 rounded-lg text-[11px]">
                      <div>
                        <span className="text-slate-400 block font-semibold">Source A ({rev.date_a || 'Date A'}):</span>
                        <span className="text-slate-200">{rev.value_a} ({rev.source_doc_a || 'Doc A'})</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block font-semibold">Source B ({rev.date_b || 'Date B'}):</span>
                        <span className="text-slate-200">{rev.value_b} ({rev.source_doc_b || 'Doc B'})</span>
                      </div>
                    </div>
                    {rev.resolution_notes && (
                      <p className="text-[11px] text-teal-300 border-t border-slate-800 pt-1.5">
                        <strong>Resolution Notes:</strong> {rev.resolution_notes}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      )}


      {/* HUMAN REVIEW MODAL */}
      {activeReviewDoc && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-2xl w-full border-teal-500/40 shadow-2xl relative max-h-[90vh] flex flex-col bg-slate-950 p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <CardTitle className="text-sm font-bold text-teal-300 flex items-center gap-2">
                  <CheckSquare className="w-4 h-4 text-teal-400" /> Staff Human Review & Indexing Approval
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  Review AI-suggested metadata and extracted text before publishing to vector search index.
                </CardDescription>
              </div>
              <button onClick={() => setActiveReviewDoc(null)} className="text-slate-400 hover:text-white p-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            {isAiSuggested && (
              <div className="p-2.5 bg-teal-950/40 border border-teal-500/40 rounded-lg text-xs text-teal-300 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-300 flex-shrink-0" />
                <span>Metadata fields pre-filled with AI suggestions. Staff review required before publishing.</span>
              </div>
            )}

            <div className="space-y-3 overflow-y-auto pr-1 flex-1 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-400 font-semibold block">Document Title:</label>
                  <input
                    type="text"
                    value={reviewTitle}
                    onChange={(e) => setReviewTitle(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-teal-500 rounded-lg p-2 text-xs text-white outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-slate-400 font-semibold block">Clinical Category (doc_type):</label>
                  <select
                    value={reviewDocType}
                    onChange={(e) => setReviewDocType(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-teal-500 rounded-lg p-2 text-xs text-white outline-none"
                  >
                    <option value="consultation">Consultation Note</option>
                    <option value="lab_report">Lab Report</option>
                    <option value="procedure">Procedure Note</option>
                    <option value="ultrasound">Ultrasound Report</option>
                    <option value="medication_record">Medication Order</option>
                    <option value="discharge_summary">Discharge Summary</option>
                    <option value="pending_lab_order">Pending Order</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-400 font-semibold block">Clinical Record Date:</label>
                  <input
                    type="date"
                    value={reviewClinicalDate}
                    onChange={(e) => setReviewClinicalDate(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-teal-500 rounded-lg p-2 text-xs text-white outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-slate-400 font-semibold block">Link to Pending Order (Explicit Confirmation):</label>
                  <select
                    value={reviewOrderId}
                    onChange={(e) => setReviewOrderId(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-teal-500 rounded-lg p-2 text-xs text-white outline-none"
                  >
                    <option value="">No pending order link</option>
                    {timeline
                      .filter((ev) => ev.event_type === 'pending_order')
                      .map((ord) => (
                        <option key={ord.id} value={ord.id}>
                          {ord.title} ({ord.event_date})
                        </option>
                      ))}
                  </select>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-slate-400 font-semibold block">Extracted Text Content for Indexing:</label>
                <textarea
                  rows={8}
                  value={reviewExtractedText}
                  onChange={(e) => setReviewExtractedText(e.target.value)}
                  placeholder="Review or edit extracted text..."
                  className="w-full bg-slate-900 border border-slate-800 focus:border-teal-500 rounded-lg p-2.5 text-xs text-slate-200 outline-none font-mono"
                />
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-2">
              <Button onClick={() => setActiveReviewDoc(null)} variant="ghost" size="sm" className="text-xs">
                Cancel
              </Button>
              <Button
                onClick={handleSaveAndPublishReview}
                disabled={isPublishing || !reviewTitle.trim()}
                variant="primary"
                size="sm"
                className="text-xs font-semibold"
              >
                {isPublishing ? <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <CheckSquare className="w-3.5 h-3.5 mr-1.5" />}
                Save & Publish to Vector Index
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* VERSION HISTORY MODAL */}
      {versionHistoryDoc && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-3xl w-full border-teal-500/40 shadow-2xl relative max-h-[90vh] flex flex-col bg-slate-950 p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <CardTitle className="text-sm font-bold text-amber-300 flex items-center gap-2">
                  <GitBranch className="w-4 h-4 text-amber-400" /> Version History — {versionHistoryDoc.title}
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  Current Version: v{versionHistoryDoc.current_version} &nbsp;|&nbsp; Category: {getDocTypeLabel(versionHistoryDoc.doc_type)}
                </CardDescription>
              </div>
              <button onClick={() => setVersionHistoryDoc(null)} className="text-slate-400 hover:text-white p-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 overflow-y-auto pr-1 flex-1 text-xs">
              {isLoadingVersions ? (
                <div className="py-12 text-center text-slate-400 space-y-2">
                  <RefreshCw className="w-6 h-6 text-teal-400 animate-spin mx-auto" />
                  <p>Loading document versions...</p>
                </div>
              ) : versionList.length === 0 ? (
                <div className="p-8 text-center text-slate-500">No previous versions recorded for this document.</div>
              ) : (
                <div className="space-y-3">
                  {versionList.map((ver) => (
                    <div key={ver.id} className="p-3 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                      <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5">
                        <div className="flex items-center gap-2">
                          <span className="font-bold font-mono text-teal-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                            v{ver.version_number}
                          </span>
                          <span className="text-slate-300 text-[11px]">
                            Engine: <b>{ver.extraction_provenance}</b>
                          </span>
                        </div>
                        <span className="text-[11px] text-slate-400 font-mono">
                          {ver.created_at ? new Date(ver.created_at).toLocaleString() : 'Recorded'}
                        </span>
                      </div>

                      {ver.diff_summary && (
                        <div className="space-y-1">
                          <span className="text-[10px] uppercase font-semibold text-slate-500">Textual Diff Comparison:</span>
                          <pre className="p-2 bg-slate-950 border border-slate-800/80 rounded font-mono text-[10px] text-slate-300 overflow-x-auto whitespace-pre-wrap max-h-24">
                            {ver.diff_summary}
                          </pre>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-800 flex justify-end">
              <Button onClick={() => setVersionHistoryDoc(null)} variant="outline" size="sm" className="text-xs">
                Close History
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* SOURCE DOCUMENT MODAL */}
      {selectedDoc && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-4xl w-full border-teal-500/30 shadow-2xl relative max-h-[90vh] flex flex-col bg-slate-950">
            <div className="flex items-center justify-between p-4 border-b border-slate-800">
              <div>
                <CardTitle className="text-base flex items-center gap-2 text-slate-100">
                  <ShieldCheck className="w-5 h-5 text-teal-400" />
                  {selectedDoc.title}
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  Clinical Date: {selectedDoc.clinical_date} &nbsp;|&nbsp; Type: {getDocTypeLabel(selectedDoc.doc_type)}
                </CardDescription>
              </div>

              <button
                onClick={closeModal}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 flex-1 overflow-y-auto space-y-4">
              {pdfLoading && (
                <div className="py-16 text-center text-slate-400 space-y-2">
                  <RefreshCw className="w-8 h-8 text-teal-400 animate-spin mx-auto" />
                  <p className="text-xs font-medium">Authenticating and fetching document file...</p>
                </div>
              )}

              {pdfError && (
                <div className="p-6 bg-rose-950/60 border border-rose-800 rounded-xl text-rose-300 text-xs space-y-3">
                  <div className="flex items-center gap-2 font-bold text-rose-200">
                    <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
                    Document Access Denied
                  </div>
                  <p>{pdfError}</p>
                  <Button
                    onClick={() => handleOpenDocumentSource(selectedDoc, targetPage)}
                    variant="outline"
                    size="sm"
                    className="text-xs border-rose-700 text-rose-200 hover:bg-rose-900/40"
                  >
                    <RefreshCw className="w-3.5 h-3.5 mr-1" /> Retry
                  </Button>
                </div>
              )}

              {selectedDoc.status === 'pending' && !pdfLoading && (
                <div className="p-8 bg-amber-950/30 border border-amber-800/60 rounded-xl text-amber-200 text-center space-y-3">
                  <Clock className="w-10 h-10 text-amber-400 mx-auto" />
                  <h4 className="text-sm font-bold text-amber-300">Result Not Yet Recorded</h4>
                  <p className="text-xs text-slate-300 max-w-md mx-auto">
                    This order was requested on {selectedDoc.clinical_date}. The reference laboratory has not yet completed processing or published the diagnostic report file.
                  </p>
                </div>
              )}

              {pdfBlobUrl && selectedDoc.status !== 'pending' && !pdfLoading && !pdfError && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                    <div className="flex items-center gap-2 text-slate-300 font-medium">
                      <span>Original document</span>
                      {targetPage > 1 && (
                        <span className="text-[10px] font-mono bg-teal-950 text-teal-300 px-2 py-0.5 rounded border border-teal-800/60">
                          Navigated to Page {targetPage}
                        </span>
                      )}
                    </div>
                    <a
                      href={pdfBlobUrl}
                      download={`${selectedDoc.title}.pdf`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1 bg-teal-500 text-slate-950 rounded font-semibold text-xs hover:bg-teal-400 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" /> Download PDF
                    </a>
                  </div>

                  {/* Embedded Authenticated Blob PDF Viewer with Page Anchor */}
                  <iframe
                    src={`${pdfBlobUrl}#page=${targetPage}&toolbar=0`}
                    title={selectedDoc.title}
                    className="w-full h-[520px] rounded-xl border border-slate-800 bg-slate-900"
                  />
                </div>
              )}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

