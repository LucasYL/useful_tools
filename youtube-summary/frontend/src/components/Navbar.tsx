'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();
  const { t, language, setLanguage } = useLanguage();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
    setMenuOpen(false);
  };

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'zh' : 'en');
  };

  useEffect(() => {
    const handleRouteChange = () => {
      setMenuOpen(false);
    };
    
    window.addEventListener('popstate', handleRouteChange);
    
    return () => {
      window.removeEventListener('popstate', handleRouteChange);
    };
  }, []);

  return (
    <nav className="sticky top-0 z-20 bg-white shadow-lg border-b border-neutral-100">
      <div className="max-w-7xl mx-auto px-6 sm:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo and main nav */}
          <div className="flex items-center">
            <Link href="/" className="flex-shrink-0 flex items-center">
              <span className="font-bold text-2xl text-neutral-800 tracking-tight">Clipnote</span>
            </Link>
          </div>

          {/* Desktop navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link 
              href="/"
              className="px-4 py-3 text-sm font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50 rounded-md transition-all"
            >
              {t('createNew')}
            </Link>
            
            {isAuthenticated && (
              <Link 
                href="/history"
                className="px-4 py-3 text-sm font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50 rounded-md transition-all"
              >
                {t('summaryHistory')}
              </Link>
            )}
            
            <button 
              onClick={toggleLanguage}
              className="px-4 py-3 text-sm font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50 rounded-md transition-all"
            >
              {language === 'en' ? '中文' : 'English'}
            </button>
            
            {isAuthenticated ? (
              <div className="relative">
                <button 
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="flex items-center px-4 py-3 text-sm font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50 rounded-md transition-all"
                >
                  <span className="mr-1">{user?.username}</span>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
                
                {menuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl py-2 z-10 border border-neutral-100">
                    <button 
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors"
                    >
                      {t('logout')}
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex space-x-3">
                <Link 
                  href="/login"
                  className="px-4 py-3 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-all"
                >
                  {t('login')}
                </Link>
                <Link 
                  href="/register"
                  className="px-4 py-3 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md shadow-sm transition-all"
                >
                  {t('register')}
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden">
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="inline-flex items-center justify-center p-3 rounded-md text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50 transition-all"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-6 w-6" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                {menuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden">
          <div className="px-4 pt-3 pb-4 space-y-2 border-t border-neutral-100 bg-white">
            <Link 
              href="/"
              className="block px-4 py-3 text-base font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50 rounded-md transition-all"
              onClick={() => setMenuOpen(false)}
            >
              {t('createNew')}
            </Link>
            
            {isAuthenticated && (
              <Link 
                href="/history"
                className="block px-4 py-3 text-base font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50 rounded-md transition-all"
                onClick={() => setMenuOpen(false)}
              >
                {t('summaryHistory')}
              </Link>
            )}
            
            <button 
              onClick={() => {
                toggleLanguage();
                setMenuOpen(false);
              }}
              className="w-full text-left block px-4 py-3 text-base font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50 rounded-md transition-all"
            >
              {language === 'en' ? '中文' : 'English'}
            </button>
            
            {isAuthenticated ? (
              <button 
                onClick={handleLogout}
                className="w-full text-left block px-4 py-3 text-base font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50 rounded-md transition-all"
              >
                {t('logout')}
              </button>
            ) : (
              <>
                <Link 
                  href="/login"
                  className="block px-4 py-3 text-base font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-all"
                  onClick={() => setMenuOpen(false)}
                >
                  {t('login')}
                </Link>
                <Link 
                  href="/register"
                  className="block px-4 py-3 text-base font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-all"
                  onClick={() => setMenuOpen(false)}
                >
                  {t('register')}
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
} 