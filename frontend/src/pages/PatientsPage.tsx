import React, { useState, useEffect } from 'react';
import { useAuth } from '../auth/AuthContext';
import { apiClient } from '../services/api';
import type { Patient, APIError } from '../types';
import { Card, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  Users, Search, Lock, AlertTriangle, Calendar, RefreshCw, Eye
} from 'lucide-react';

interface PatientsPageProps {
  onSelectPatient: (patientId: string) => void;
}

export const PatientsPage: React.FC<PatientsPageProps> = ({ onSelectPatient }) => {
  const { token, staff } = useAuth();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<APIError | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

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
    let isCancelled = false;

    setPatients([]);
    setError(null);

    if (!token) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    apiClient.getPatients(token)
      .then((res) => {
        if (!isCancelled) {
          setPatients(res.patients);
        }
      })
      .catch((err) => {
        if (!isCancelled) {
          setError(err as APIError);
        }
      })
      .finally(() => {
        if (!isCancelled) {
          setIsLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [token]);

  const filteredPatients = patients.filter((p) => {
    const q = searchQuery.toLowerCase();
    return (
      p.first_name.toLowerCase().includes(q) ||
      p.last_name.toLowerCase().includes(q) ||
      p.mrn.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-4">
      {/* Patient Directory Grid Card */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <CardTitle className="text-xl">
                <Users className="w-5 h-5 text-teal-400" />
                Patient Directory
              </CardTitle>
              <CardDescription>
                Authorized synthetic patient records assigned to your staff account.
              </CardDescription>
            </div>

            <div className="flex items-center gap-3">
              {/* Search Bar */}
              <div className="relative w-full sm:w-64">
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by name or MRN..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
                />
              </div>

              <Button onClick={fetchPatients} variant="outline" size="sm" isLoading={isLoading} className="flex-shrink-0">
                <RefreshCw className="w-3.5 h-3.5 mr-1" />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>

        {/* Loading State */}
        {isLoading && (
          <div className="p-12 text-center text-slate-400 space-y-2">
            <RefreshCw className="w-6 h-6 text-teal-400 animate-spin mx-auto" />
            <p className="text-xs">Loading authorized patient records...</p>
          </div>
        )}

        {/* Error State */}
        {!isLoading && error && (
          <div className="p-6 bg-rose-950/40 border border-rose-900/60 rounded-lg text-rose-300 text-xs flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0" />
            <div>
              <strong className="block text-rose-200 font-semibold mb-1">Unable to Load Patients</strong>
              {error.message}
            </div>
          </div>
        )}

        {/* Empty Result */}
        {!isLoading && !error && filteredPatients.length === 0 && (
          <div className="p-12 text-center space-y-3">
            <Lock className="w-10 h-10 text-slate-600 mx-auto" />
            <h4 className="text-sm font-semibold text-slate-300">No Patient Records Found</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Your staff account (<code className="text-teal-300">{staff?.role}</code>) does not hold access grants for this query.
            </p>
          </div>
        )}

        {/* Patient List */}
        {!isLoading && !error && filteredPatients.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
            {filteredPatients.map((patient) => (
              <div
                key={patient.id}
                onClick={() => onSelectPatient(patient.id)}
                className="bg-slate-900/90 hover:bg-slate-900 border border-slate-800 hover:border-teal-500/50 rounded-xl p-4 cursor-pointer transition-all duration-200 space-y-3 shadow-md hover:shadow-teal-950/20 group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-teal-400 bg-teal-950/80 px-2 py-0.5 rounded border border-teal-800/60">
                    {patient.mrn}
                  </span>
                  <Badge variant="success">Active</Badge>
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

                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-end text-xs font-medium text-teal-400 group-hover:text-teal-300">
                  <span className="flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                    Open Patient Workspace <Eye className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
