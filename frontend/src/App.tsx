import React, { useState } from 'react';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { PatientsPage } from './pages/PatientsPage';
import { SetupPage } from './pages/SetupPage';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { ShieldCheck, Users, Server, LogOut, UserCheck } from 'lucide-react';

const MainLayout: React.FC = () => {
  const { staff, logout, token } = useAuth();
  const [activeTab, setActiveTab] = useState<'directory' | 'setup'>('directory');

  if (!token || !staff) {
    return <LoginPage />;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between p-4 sm:p-8">
      {/* Header Bar */}
      <header className="max-w-6xl w-full mx-auto flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-800/80 gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-teal-500/20">
            <ShieldCheck className="w-6 h-6 text-slate-950" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-white via-slate-200 to-teal-400 bg-clip-text text-transparent">
              CareLens AI
            </h1>
            <p className="text-xs text-slate-400">Synthetic Patient EHR Insight Engine • Milestone 2 Auth & Directory</p>
          </div>
        </div>

        {/* Navigation Tabs & Staff Identity */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="bg-slate-900 p-1 rounded-lg border border-slate-800 flex items-center text-xs">
            <button
              onClick={() => setActiveTab('directory')}
              className={`px-3 py-1.5 rounded-md font-medium transition-colors flex items-center gap-1.5 ${
                activeTab === 'directory'
                  ? 'bg-teal-500 text-slate-950 font-semibold shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              Patient Directory
            </button>
            <button
              onClick={() => setActiveTab('setup')}
              className={`px-3 py-1.5 rounded-md font-medium transition-colors flex items-center gap-1.5 ${
                activeTab === 'setup'
                  ? 'bg-teal-500 text-slate-950 font-semibold shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Server className="w-3.5 h-3.5" />
              Setup & Health Verifier
            </button>
          </div>

          <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
            <Badge variant="success" className="flex items-center gap-1">
              <UserCheck className="w-3 h-3" />
              {staff.full_name.split(' ')[0]} ({staff.role})
            </Badge>
            <Button onClick={logout} variant="outline" size="sm">
              <LogOut className="w-3.5 h-3.5 mr-1" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-6xl w-full mx-auto my-8">
        {activeTab === 'directory' ? <PatientsPage /> : <SetupPage />}
      </main>

      {/* Footer */}
      <footer className="max-w-6xl w-full mx-auto pt-6 border-t border-slate-800/80 text-center text-xs text-slate-500">
        CareLens AI Solo Development • Developer: Varun Yadav T • Milestone 2 Verified
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
