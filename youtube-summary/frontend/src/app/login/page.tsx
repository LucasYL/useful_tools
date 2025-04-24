'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { login, error, loading } = useAuth();
  const router = useRouter();
  const { t } = useLanguage();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await login(username, password);
      router.push('/'); // 登录成功后跳转到首页
    } catch (err) {
      // 错误已在AuthContext中处理
      console.error('Login form submission error:', err);
    }
  };

  return (
    <main className="min-h-screen bg-neutral-50 flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-xl shadow-sm border border-neutral-200 p-8">
          <h1 className="text-2xl font-semibold text-center mb-6">
            {t('login')}
          </h1>
          
          {error && (
            <div className="p-3 mb-4 rounded-lg bg-red-50 border border-red-200 text-center">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-neutral-700 mb-1">
                {t('username')}
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
                required
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-neutral-700 mb-1">
                {t('password')}
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
                  required
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 px-3 text-neutral-600"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
            >
              {loading ? t('loggingIn') : t('login')}
            </button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-sm text-neutral-600">
              {t('noAccount')}{' '}
              <Link href="/register" className="text-blue-600 hover:text-blue-800 font-medium">
                {t('signUp')}
              </Link>
            </p>
          </div>
        </div>
        
        <div className="mt-4 text-center">
          <Link href="/" className="text-sm text-neutral-600 hover:text-neutral-900">
            &larr; {t('backToHome')}
          </Link>
        </div>
      </div>
    </main>
  );
} 