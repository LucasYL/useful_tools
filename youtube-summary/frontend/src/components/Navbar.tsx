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
    <nav className="sticky top-0 z-20 bg-white shadow-sm border-b border-neutral-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex justify-between items-center h-16">
          {/* Logo and main nav */}
          <div className="flex items-center">
            <Link href="/" className="flex-shrink-0 flex items-center">
              <span className="font-bold text-xl text-neutral-900">Clipnote</span>
            </Link>
          </div>

          {/* Desktop navigation */}
          <div className="hidden md:flex items-center space-x-4">
            <Link 
              href="/"
              className="px-3 py-2 text-sm font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 rounded-md"
            >
              {t('createNew')}
            </Link>
            
            {isAuthenticated && (
              <Link 
                href="/history"
                className="px-3 py-2 text-sm font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 rounded-md"
              >
                {t('summaryHistory')}
              </Link>
            )}
            
            <button 
              onClick={toggleLanguage}
              className="px-3 py-2 text-sm font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 rounded-md"
            >
              {language === 'en' ? '中文' : 'English'}
            </button>
            
            {isAuthenticated ? (
              <div className="relative">
                <button 
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="flex items-center px-3 py-2 text-sm font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 rounded-md"
                >
                  <span className="mr-1">{user?.username}</span>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
                
                {menuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 border border-neutral-200">
                    <button 
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-100"
                    >
                      {t('logout')}
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex space-x-2">
                <Link 
                  href="/login"
                  className="px-3 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md"
                >
                  {t('login')}
                </Link>
                <Link 
                  href="/register"
                  className="px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
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
              className="inline-flex items-center justify-center p-2 rounded-md text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100"
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
          <div className="px-2 pt-2 pb-3 space-y-1 border-t border-neutral-200">
            <Link 
              href="/"
              className="block px-3 py-2 text-base font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 rounded-md"
              onClick={() => setMenuOpen(false)}
            >
              {t('createNew')}
            </Link>
            
            {isAuthenticated && (
              <Link 
                href="/history"
                className="block px-3 py-2 text-base font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 rounded-md"
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
              className="w-full text-left block px-3 py-2 text-base font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 rounded-md"
            >
              {language === 'en' ? '中文' : 'English'}
            </button>
            
            {isAuthenticated ? (
              <button 
                onClick={handleLogout}
                className="w-full text-left block px-3 py-2 text-base font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 rounded-md"
              >
                {t('logout')}
              </button>
            ) : (
              <>
                <Link 
                  href="/login"
                  className="block px-3 py-2 text-base font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md"
                  onClick={() => setMenuOpen(false)}
                >
                  {t('login')}
                </Link>
                <Link 
                  href="/register"
                  className="block px-3 py-2 text-base font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
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