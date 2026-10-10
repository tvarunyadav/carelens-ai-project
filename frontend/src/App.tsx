import React, { useState } from 'react';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { PatientsPage } from './pages/PatientsPage';
import { PatientWorkspacePage } from './pages/PatientWorkspacePage';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { ShieldCheck, Users, LogOut, UserCheck } from 'lucide-react';

const MainLayout: React.FC = () => {
  const { staff, logout, token } = useAuth();
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);

  if (!token || !staff) {
    return <LoginPage />;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between p-4 sm:p-8">
      {/* Shared Application Header */}
      <header className="max-w-6xl w-full mx-auto flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-800/80 gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-teal-500/20 flex-shrink-0">
            <ShieldCheck className="w-6 h-6 text-slate-950" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-white via-slate-200 to-teal-400 bg-clip-text text-transparent">
              CareLens AI
            </h1>
            <p className="text-xs text-slate-400">Patient History Assistant</p>
          </div>
        </div>

        {/* Header Action Controls & Staff Identity */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 flex items-center gap-2 text-xs">
            <Users className="w-3.5 h-3.5 text-teal-400" />
            <span className="font-semibold text-slate-200">
              {selectedPatientId ? 'Patient Workspace' : 'Patient Directory'}
            </span>
          </div>

          <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
            <Badge variant="success" className="flex items-center gap-1 font-medium">
              <UserCheck className="w-3 h-3" />
              {staff.full_name} ({staff.role})
            </Badge>
            <Button onClick={logout} variant="outline" size="sm">
              <LogOut className="w-3.5 h-3.5 mr-1" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Experience */}
      <main className="max-w-6xl w-full mx-auto my-6">
        {selectedPatientId ? (
          <PatientWorkspacePage
            patientId={selectedPatientId}
            onBack={() => setSelectedPatientId(null)}
          />
        ) : (
          <PatientsPage onSelectPatient={(id) => setSelectedPatientId(id)} />
        )}
      </main>

      {/* Footer */}
      <footer className="max-w-6xl w-full mx-auto pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500">
        <span>CareLens AI Platform</span>
        <span className="flex items-center gap-1 text-[11px] bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
          <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
          Synthetic Demo Data Only
        </span>
      </footer>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
}

export default App;
