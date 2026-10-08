import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { ShieldCheck, LogIn, AlertCircle, Info } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { loginWithSupabase, isLoading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setLocalError('Please enter both clinic email address and password.');
      return;
    }
    setLocalError(null);
    try {
      await loginWithSupabase(email, password);
    } catch (err: any) {
      // Handled in context
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center p-4">
      <div className="max-w-md w-full space-y-6">
        {/* Brand Logo */}
        <div className="text-center space-y-2">
          <div className="inline-flex w-12 h-12 rounded-2xl bg-gradient-to-tr from-teal-500 to-cyan-500 items-center justify-center shadow-lg shadow-teal-500/20">
            <ShieldCheck className="w-7 h-7 text-slate-950" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-white via-slate-200 to-teal-400 bg-clip-text text-transparent">
            CareLens AI
          </h1>
          <p className="text-xs text-slate-400">
            Authorized Clinic Staff Portal • Supabase Auth Authentication
          </p>
        </div>

        <Card className="border-teal-500/20 shadow-2xl">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>
                <LogIn className="w-5 h-5 text-teal-400" />
                Staff Sign In
              </CardTitle>
              <Badge variant="info">Supabase Auth</Badge>
            </div>
            <CardDescription>
              Enter your verified clinic credentials to access authorized patient EHR records.
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            {(error || localError) && (
              <div className="bg-rose-950/60 border border-rose-800/80 rounded-lg p-3 text-xs text-rose-300 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                <span>{localError || error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Clinic Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="dr.alice@clinic.org"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              isLoading={isLoading}
              className="w-full"
            >
              Sign In
            </Button>
          </form>

          {/* Setup Guidance Box */}
          <div className="mt-6 pt-4 border-t border-slate-800/80 space-y-2 text-xs text-slate-400">
            <div className="flex items-center gap-1.5 font-semibold text-slate-300">
              <Info className="w-4 h-4 text-teal-400" />
              Staff Account Setup Notice
            </div>
            <p className="text-[11px] leading-relaxed text-slate-400">
              Sign-in requires a staff account registered in Supabase Auth and assigned a role in <code className="text-teal-300">public.staff_profiles</code>. Follow the migration and user creation steps in <code className="text-slate-300">docs/milestone-2-setup.md</code>.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};
