import React from 'react';
import { useHealthCheck } from '../hooks/useHealthCheck';
import { Button } from './ui/button';
import { Card, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Badge } from './ui/badge';
import { Server, Activity, AlertTriangle, CheckCircle2, RefreshCw, Clock, Network } from 'lucide-react';

export const HealthCheckCard: React.FC = () => {
  const { status, data, error, lastCheckedAt, checkHealth } = useHealthCheck();

  return (
    <Card className="max-w-xl w-full border-teal-500/20 shadow-2xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>
            <Server className="w-5 h-5 text-teal-400" />
            Backend Connection Verifier
          </CardTitle>
          <Badge variant={status === 'success' ? 'success' : status === 'error' ? 'error' : status === 'loading' ? 'warning' : 'neutral'}>
            {status === 'success' && <><CheckCircle2 className="w-3.5 h-3.5" /> Online</>}
            {status === 'error' && <><AlertTriangle className="w-3.5 h-3.5" /> Offline / Error</>}
            {status === 'loading' && <><RefreshCw className="w-3.5 h-3.5 animate-spin" /> Checking...</>}
            {status === 'idle' && <><Activity className="w-3.5 h-3.5" /> Unchecked</>}
          </Badge>
        </div>
        <CardDescription>
          Tests explicit localhost CORS, endpoint response time, and FastAPI <code className="text-teal-300">GET /health</code> contract readiness.
        </CardDescription>
      </CardHeader>

      <div className="space-y-4">
        {/* Endpoint details bar */}
        <div className="bg-slate-900/90 rounded-lg p-3 border border-slate-800 text-xs font-mono flex items-center justify-between text-slate-300">
          <span className="flex items-center gap-2">
            <Network className="w-4 h-4 text-cyan-400" />
            <span className="text-slate-400">Target Endpoint:</span> http://localhost:8000/health
          </span>
          <span className="text-slate-500 text-[10px]">CORS Enabled</span>
        </div>

        {/* Action Button */}
        <div className="flex items-center gap-3">
          <Button
            onClick={checkHealth}
            isLoading={status === 'loading'}
            variant="primary"
            className="w-full sm:w-auto"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Check Backend Status
          </Button>

          {lastCheckedAt && (
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              Checked at {lastCheckedAt}
            </span>
          )}
        </div>

        {/* State Display: Success */}
        {status === 'success' && data && (
          <div className="bg-emerald-950/40 border border-emerald-800/60 rounded-xl p-4 text-sm animate-fadeIn space-y-2">
            <div className="flex items-center justify-between text-emerald-300 font-medium">
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Backend Endpoint Operational
              </span>
              <span className="text-xs text-emerald-400/80 font-mono">200 OK</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-emerald-900/50 text-slate-300">
              <div><span className="text-slate-400">Service:</span> {data.service}</div>
              <div><span className="text-slate-400">Version:</span> {data.version}</div>
              <div className="col-span-2 truncate"><span className="text-slate-400">Timestamp:</span> {data.timestamp}</div>
            </div>
          </div>
        )}

        {/* State Display: Error / Timeout */}
        {status === 'error' && error && (
          <div className="bg-rose-950/40 border border-rose-800/60 rounded-xl p-4 text-sm animate-fadeIn space-y-2">
            <div className="flex items-center gap-2 text-rose-300 font-medium">
              <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
              <span>Connection Failed</span>
            </div>
            <p className="text-xs text-rose-200/80">{error.message}</p>
            <div className="text-[11px] text-slate-400 pt-1 border-t border-rose-900/40">
              <strong>Tip:</strong> Ensure FastAPI is running on port 8000 using command:<br />
              <code className="text-teal-300 bg-slate-900 px-1.5 py-0.5 rounded text-[11px]">
                uvicorn app.main:app --reload --port 8000
              </code>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};
