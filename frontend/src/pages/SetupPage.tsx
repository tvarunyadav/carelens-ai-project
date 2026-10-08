import React from 'react';
import { HealthCheckCard } from '../components/HealthCheckCard';
import { Card, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { ShieldCheck, FileText, Database, Cpu, Layers, GitBranch, Terminal } from 'lucide-react';

export const SetupPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between p-4 sm:p-8">
      {/* Header Bar */}
      <header className="max-w-6xl w-full mx-auto flex items-center justify-between pb-6 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-teal-500/20">
            <ShieldCheck className="w-6 h-6 text-slate-950" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-white via-slate-200 to-teal-400 bg-clip-text text-transparent">
              CareLens AI
            </h1>
            <p className="text-xs text-slate-400">Synthetic Patient EHR Insight Engine • Milestone 1 Foundation</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="info">Solo Project</Badge>
          <Badge variant="success">Milestone 1</Badge>
        </div>
      </header>

      {/* Main Grid */}
      <main className="max-w-6xl w-full mx-auto my-8 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Health Check & System Status */}
        <section className="lg:col-span-6 space-y-6">
          <HealthCheckCard />

          <Card>
            <CardHeader>
              <CardTitle>
                <Layers className="w-5 h-5 text-cyan-400" />
                Validated Shared Contracts
              </CardTitle>
              <CardDescription>
                Pydantic models and TypeScript interfaces defined once to guarantee end-to-end type safety.
              </CardDescription>
            </CardHeader>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 flex items-center gap-2 text-slate-300">
                <FileText className="w-4 h-4 text-teal-400" /> Patient
              </div>
              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 flex items-center gap-2 text-slate-300">
                <Cpu className="w-4 h-4 text-cyan-400" /> Question
              </div>
              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 flex items-center gap-2 text-slate-300">
                <ShieldCheck className="w-4 h-4 text-emerald-400" /> Claim
              </div>
              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 flex items-center gap-2 text-slate-300">
                <GitBranch className="w-4 h-4 text-purple-400" /> Citation
              </div>
              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 flex items-center gap-2 text-slate-300 col-span-2">
                <Database className="w-4 h-4 text-amber-400" /> TimelineEvent
              </div>
            </div>
          </Card>
        </section>

        {/* Right Column: Architecture & Stack Blueprint */}
        <section className="lg:col-span-6 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>
                <Terminal className="w-5 h-5 text-teal-400" />
                Stack & Module Boundaries
              </CardTitle>
              <CardDescription>
                Clean separation of concerns with explicit CORS and zero secret exposure.
              </CardDescription>
            </CardHeader>

            <ul className="space-y-3 text-xs text-slate-300">
              <li className="flex items-start gap-2 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                <span className="w-2 h-2 rounded-full bg-teal-400 mt-1.5 flex-shrink-0" />
                <div>
                  <strong className="text-slate-100">Frontend:</strong> React 19 + Vite + TypeScript + Tailwind CSS + shadcn design components.
                </div>
              </li>
              <li className="flex items-start gap-2 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                <span className="w-2 h-2 rounded-full bg-cyan-400 mt-1.5 flex-shrink-0" />
                <div>
                  <strong className="text-slate-100">Backend:</strong> Python 3.11 + FastAPI + Pydantic + pydantic-settings.
                </div>
              </li>
              <li className="flex items-start gap-2 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                <span className="w-2 h-2 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                <div>
                  <strong className="text-slate-100">Security & Isolation:</strong> Strict authorization checks before service logic; secrets backend-only.
                </div>
              </li>
              <li className="flex items-start gap-2 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                <span className="w-2 h-2 rounded-full bg-purple-400 mt-1.5 flex-shrink-0" />
                <div>
                  <strong className="text-slate-100">Future Infrastructure:</strong> Supabase PostgreSQL (pgvector), Supabase Storage, local Sentence Transformers, Gemini + Groq LLM adapters.
                </div>
              </li>
            </ul>
          </Card>
        </section>
      </main>

      {/* Footer */}
      <footer className="max-w-6xl w-full mx-auto pt-6 border-t border-slate-800/80 text-center text-xs text-slate-500">
        CareLens AI Solo Development • Developer: Varun Yadav T • Milestone 1 Complete
      </footer>
    </div>
  );
};
