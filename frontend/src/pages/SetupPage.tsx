import React from 'react';
import { HealthCheckCard } from '../components/HealthCheckCard';
import { Card, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { ShieldCheck, Database, Layers, Cpu } from 'lucide-react';

export const SetupPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* System Status Section */}
      <section className="flex flex-col items-center gap-6">
        <HealthCheckCard />

        <Card className="max-w-xl w-full">
          <CardHeader>
            <CardTitle>
              <Layers className="w-5 h-5 text-teal-400" />
              Service Overview
            </CardTitle>
            <CardDescription>
              Core platform modules and access authorization layers.
            </CardDescription>
          </CardHeader>
          <div className="grid grid-cols-2 gap-3 text-xs font-mono">
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 flex items-center gap-2 text-slate-300">
              <ShieldCheck className="w-4 h-4 text-teal-400 flex-shrink-0" />
              <span>Identity & Auth</span>
            </div>
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 flex items-center gap-2 text-slate-300">
              <Database className="w-4 h-4 text-cyan-400 flex-shrink-0" />
              <span>Patient Directory</span>
            </div>
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 flex items-center gap-2 text-slate-300">
              <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>Patient Access Grants</span>
            </div>
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 flex items-center gap-2 text-slate-300">
              <Cpu className="w-4 h-4 text-purple-400 flex-shrink-0" />
              <span>Audit Logging</span>
            </div>
          </div>
        </Card>
      </section>
    </div>
  );
};
