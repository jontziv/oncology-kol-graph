import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const { signUp, logIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isSignUp) {
        await signUp(email, password);
      } else {
        await logIn(email, password);
      }
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-slate-900 border-slate-800">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Oncology KOL Graph</CardTitle>
          <CardDescription>
            {isSignUp ? 'Create an account' : 'Sign in to your account'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
                required
              />
            </div>

            {error && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-md text-rose-400 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-sky-600 hover:bg-sky-700 disabled:bg-slate-700 text-white font-medium rounded-md transition-colors"
            >
              {loading ? 'Loading...' : isSignUp ? 'Sign Up' : 'Log In'}
            </button>

            <div className="text-center">
              <button
                type="button"
                onClick={() => setIsSignUp(!isSignUp)}
                className="text-sm text-sky-400 hover:text-sky-300"
              >
                {isSignUp ? 'Already have an account? Log in' : "Don't have an account? Sign up"}
              </button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
