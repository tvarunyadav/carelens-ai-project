import React, { useState, useEffect } from 'react';
import { useAuth } from '../auth/AuthContext';
import { apiClient } from '../services/api';
import type { Patient, APIError } from '../types';
import { Card, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  Users,
  Search,
  Lock,
  UserCheck,
  AlertTriangle,
  FileText,
  Calendar,
  ShieldCheck,
  RefreshCw,
  X,
  Eye
} from 'lucide-react';

export const PatientsPage: React.FC = () => {
  const { token, staff } = useAuth();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<APIError | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const fetchPatients = async () => {
    if (!token) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiClient.getPatients(token);
      setPatients(res.patients);
    } catch (err: any) {
      setError(err as APIError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [token]);

  const handleSelectPatient = async (patientId: string) => {
    if (!token) return;
    setDetailLoading(true);
    setDetailError(null);
    setSelectedPatient(null);
    try {
      const detail = await apiClient.getPatientDetail(patientId, token);
      setSelectedPatient(detail);
    } catch (err: any) {
      setDetailError(err.message || 'Access denied for requested patient record');
    } finally {
      setDetailLoading(false);
    }
  };

  const filteredPatients = patients.filter((p) => {
    const q = searchQuery.toLowerCase();
    return (
      p.first_name.toLowerCase().includes(q) ||
      p.last_name.toLowerCase().includes(q) ||
      p.mrn.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      {/* Top Banner: Staff Grant Summary */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal-950 border border-teal-800/60 flex items-center justify-center">
            <UserCheck className="w-5 h-5 text-teal-400" />
          </div>
          <div>
            <div className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              {staff?.full_name}
              <Badge variant={staff?.role === 'doctor' ? 'success' : staff?.role === 'coordinator' ? 'info' : 'warning'}>
                {staff?.role.toUpperCase()}
              </Badge>
            </div>
            <div className="text-xs text-slate-400">
              Identity Verified via Supabase Bearer JWT • {staff?.email}
            </div>
          </div>
        </div>

        <Button onClick={fetchPatients} variant="outline" size="sm" isLoading={isLoading}>
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Refresh Directory
        </Button>
      </div>

      {/* Patient Directory Grid */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <CardTitle>
                <Users className="w-5 h-5 text-teal-400" />
                Authorized Patient Directory
              </CardTitle>
              <CardDescription>
                Displays only synthetic patient records for which your account holds an explicit read grant.
              </CardDescription>
            </div>

            {/* Search Bar */}
            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Filter by name or MRN..."
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
              />
            </div>
          </div>
        </CardHeader>

        {/* Loading State */}
        {isLoading && (
          <div className="p-8 text-center text-slate-400 space-y-2">
            <RefreshCw className="w-6 h-6 text-teal-400 animate-spin mx-auto" />
            <p className="text-xs">Authenticating token & querying authorized patient grants...</p>
          </div>
        )}

        {/* Error State */}
        {!isLoading && error && (
          <div className="p-6 bg-rose-950/40 border border-rose-900/60 rounded-lg text-rose-300 text-xs flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0" />
            <div>
              <strong className="block text-rose-200 font-semibold mb-1">Directory Fetch Error</strong>
              {error.message}
            </div>
          </div>
        )}

        {/* Empty Permitted Patients Result */}
        {!isLoading && !error && filteredPatients.length === 0 && (
          <div className="p-12 text-center space-y-3">
            <Lock className="w-10 h-10 text-slate-600 mx-auto" />
            <h4 className="text-sm font-semibold text-slate-300">Zero Permitted Patient Records</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Your verified staff account (<code className="text-teal-300">{staff?.role}</code>) does not hold explicit patient grants for this view.
              <br />
              <span className="text-[11px] text-slate-500 mt-1 block">
                CareLens AI enforces patient-level isolation: even Admin roles require explicit patient grants to access clinical EHR data.
              </span>
            </p>
          </div>
        )}

        {/* Patient List */}
        {!isLoading && !error && filteredPatients.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
            {filteredPatients.map((patient) => (
              <div
                key={patient.id}
                onClick={() => handleSelectPatient(patient.id)}
                className="bg-slate-900/90 hover:bg-slate-900 border border-slate-800 hover:border-teal-500/50 rounded-xl p-4 cursor-pointer transition-all duration-200 space-y-3 shadow-md hover:shadow-teal-950/20 group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-teal-400 bg-teal-950/80 px-2 py-0.5 rounded border border-teal-800/60">
                    {patient.mrn}
                  </span>
                  <Badge variant="success">Active File</Badge>
                </div>

                <div>
                  <h4 className="text-base font-bold text-slate-100 group-hover:text-teal-300 transition-colors">
                    {patient.first_name} {patient.last_name}
                  </h4>
                  <div className="text-xs text-slate-400 flex items-center gap-3 mt-1">
                    <span>{patient.gender}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      DOB: {patient.dob}
                    </span>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                  <span>Rev Version: v{patient.record_version}</span>
                  <span className="text-teal-400 font-medium flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                    Inspect EHR Record <Eye className="w-3 h-3" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Patient Detail Inspection Panel / Modal */}
      {(selectedPatient || detailLoading || detailError) && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-lg w-full border-teal-500/30 shadow-2xl relative animate-fadeIn">
            <button
              onClick={() => {
                setSelectedPatient(null);
                setDetailError(null);
              }}
              className="absolute right-4 top-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <CardHeader>
              <CardTitle>
                <ShieldCheck className="w-5 h-5 text-teal-400" />
                Patient Record Detail
              </CardTitle>
              <CardDescription>
                Authorized detail response from GET /api/v1/patients/{'{id}'}
              </CardDescription>
            </CardHeader>

            {detailLoading && (
              <div className="py-8 text-center text-slate-400 space-y-2">
                <RefreshCw className="w-6 h-6 text-teal-400 animate-spin mx-auto" />
                <p className="text-xs">Authorizing patient grant & loading record detail...</p>
              </div>
            )}

            {detailError && (
              <div className="p-4 bg-rose-950/60 border border-rose-800 rounded-lg text-xs text-rose-300 space-y-2">
                <div className="flex items-center gap-2 font-semibold text-rose-200">
                  <AlertTriangle className="w-4 h-4 text-rose-400" />
                  Access Authorization Error
                </div>
                <p>{detailError}</p>
              </div>
            )}

            {selectedPatient && !detailLoading && (
              <div className="space-y-4 text-xs text-slate-300">
                <div className="bg-slate-900 p-4 rounded-xl border border-slate-800 space-y-2 font-mono">
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">Patient ID:</span>
                    <span className="text-teal-300 font-semibold">{selectedPatient.id}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">MRN:</span>
                    <span className="text-slate-100">{selectedPatient.mrn}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">Full Name:</span>
                    <span className="text-slate-100 font-sans font-bold">{selectedPatient.first_name} {selectedPatient.last_name}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">Date of Birth:</span>
                    <span className="text-slate-100">{selectedPatient.dob}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">Gender:</span>
                    <span className="text-slate-100">{selectedPatient.gender}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Record Version:</span>
                    <span className="text-cyan-400 font-bold">v{selectedPatient.record_version}</span>
                  </div>
                </div>

                <div className="bg-teal-950/40 border border-teal-800/60 rounded-xl p-3 text-[11px] text-teal-300 flex items-start gap-2">
                  <FileText className="w-4 h-4 text-teal-400 flex-shrink-0 mt-0.5" />
                  <span>
                    <strong>Milestone 2 Verified:</strong> Clinical access granted to staff ID <code className="text-white">{staff?.id}</code>. Future milestones will connect PDF upload, embeddings, and evidence viewer for this patient.
                  </span>
                </div>
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
};
