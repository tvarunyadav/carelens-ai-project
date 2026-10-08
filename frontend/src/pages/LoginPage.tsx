import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { ShieldCheck, LogIn, UserCheck, AlertCircle, Sparkles } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { loginWithSupabase, loginAsDevUser, isLoading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setLocalError('Please enter both email and password.');
      return;
    }
    setLocalError(null);
    try {
      await loginWithSupabase(email, password);
    } catch (err: any) {
      // Handled in context
    }
  };

  const handleDevLogin = async (key: 'dev_user_alice' | 'dev_user_bob' | 'dev_user_admin') => {
    setLocalError(null);
    await loginAsDevUser(key);
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
            Authorized Clinic Staff Authentication Portal • Milestone 2
          </p>
        </div>

        <Card className="border-teal-500/20 shadow-2xl">
          <CardHeader>
            <CardTitle>
              <LogIn className="w-5 h-5 text-teal-400" />
              Staff Sign In
            </CardTitle>
            <CardDescription>
              Enter your credentials to access authorized synthetic patient records.
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
                placeholder="staff@clinic.org"
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
              Sign In with Supabase Auth
            </Button>
          </form>

          {/* Quick Staff Account Switcher Banner */}
          <div className="mt-6 pt-4 border-t border-slate-800/80 space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                Local Dev Quick-Switch
              </span>
              <Badge variant="neutral">Milestone 2 Demo</Badge>
            </div>

            <div className="grid grid-cols-1 gap-2">
              <button
                type="button"
                onClick={() => handleDevLogin('dev_user_alice')}
                className="text-left bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-teal-500/50 p-2.5 rounded-lg text-xs transition-colors flex items-center justify-between group"
              >
                <div>
                  <div className="font-semibold text-slate-200 group-hover:text-teal-300">
                    Dr. Alice Morgan
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Role: <span className="text-teal-400">Doctor</span> • Grants: Eleanor Vane, Marcus Chen
                  </div>
                </div>
                <UserCheck className="w-4 h-4 text-slate-500 group-hover:text-teal-400" />
              </button>

              <button
                type="button"
                onClick={() => handleDevLogin('dev_user_bob')}
                className="text-left bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-cyan-500/50 p-2.5 rounded-lg text-xs transition-colors flex items-center justify-between group"
              >
                <div>
                  <div className="font-semibold text-slate-200 group-hover:text-cyan-300">
                    Bob Vance
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Role: <span className="text-cyan-400">Coordinator</span> • Grants: Sophia Patel only
                  </div>
                </div>
                <UserCheck className="w-4 h-4 text-slate-500 group-hover:text-cyan-400" />
              </button>

              <button
                type="button"
                onClick={() => handleDevLogin('dev_user_admin')}
                className="text-left bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-purple-500/50 p-2.5 rounded-lg text-xs transition-colors flex items-center justify-between group"
              >
                <div>
                  <div className="font-semibold text-slate-200 group-hover:text-purple-300">
                    Sam Admin
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Role: <span className="text-purple-400">Admin</span> • Grants: 0 clinical records (isolation test)
                  </div>
                </div>
                <UserCheck className="w-4 h-4 text-slate-500 group-hover:text-purple-400" />
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
