'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';

// API基础URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://useful-tools.onrender.com';

// 摘要类型定义
interface Summary {
  id: number;
  video_id: string;
  video_title: string;
  summary_text: string;
  summary_type: string;
  language: string;
  created_at: string;
  is_favorite: boolean;
}

export default function History() {
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [favoriteOnly, setFavoriteOnly] = useState(false);
  
  const { isAuthenticated, token } = useAuth();
  const router = useRouter();
  const { t } = useLanguage();

  // 加载摘要数据
  useEffect(() => {
    const fetchSummaries = async () => {
      if (!isAuthenticated || !token) {
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`${API_BASE_URL}/api/summaries/`, {
          headers: {
            Authorization: `Bearer ${token}`
          },
          params: {
            favorite_only: favoriteOnly
          }
        });
        
        setSummaries(response.data);
      } catch (err: any) {
        console.error('Failed to fetch summaries:', err);
        setError(err.response?.data?.detail || t('failedToLoadHistory'));
      } finally {
        setLoading(false);
      }
    };

    fetchSummaries();
  }, [isAuthenticated, token, favoriteOnly]);

  // 处理收藏切换
  const handleToggleFavorite = async (summaryId: number) => {
    if (!token) return;
    
    try {
      const response = await axios.patch(
        `${API_BASE_URL}/api/summaries/${summaryId}/favorite`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      // 更新本地状态
      setSummaries(prevSummaries => 
        prevSummaries.map(summary => 
          summary.id === summaryId 
            ? { ...summary, is_favorite: response.data.is_favorite }
            : summary
        )
      );
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  // 处理删除摘要
  const handleDelete = async (summaryId: number) => {
    if (!token) return;
    
    if (window.confirm(t('confirmDelete'))) {
      try {
        await axios.delete(`${API_BASE_URL}/api/summaries/${summaryId}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        // 从列表中移除已删除的摘要
        setSummaries(prevSummaries => 
          prevSummaries.filter(summary => summary.id !== summaryId)
        );
      } catch (err) {
        console.error('Failed to delete summary:', err);
      }
    }
  };

  // 未登录时显示提示
  if (!isAuthenticated) {
    return (
      <main className="min-h-screen bg-neutral-50 p-4">
        <div className="max-w-4xl mx-auto mt-16 text-center">
          <h1 className="text-2xl font-semibold mb-4">{t('loginRequired')}</h1>
          <p className="mb-6 text-neutral-600">{t('loginToViewHistory')}</p>
          <div className="flex justify-center gap-4">
            <Link href="/login" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              {t('login')}
            </Link>
            <Link href="/" className="px-4 py-2 bg-neutral-200 text-neutral-800 rounded-lg hover:bg-neutral-300 transition-colors">
              {t('backToHome')}
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-neutral-50 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold">{t('summaryHistory')}</h1>
          <Link href="/" className="text-sm text-neutral-600 hover:text-neutral-900">
            &larr; {t('backToHome')}
          </Link>
        </div>
        
        {/* 过滤器 */}
        <div className="mb-6 flex justify-between items-center">
          <div className="flex items-center">
            <label className="flex items-center text-sm text-neutral-700">
              <input
                type="checkbox"
                checked={favoriteOnly}
                onChange={() => setFavoriteOnly(!favoriteOnly)}
                className="mr-2 h-4 w-4 rounded border-neutral-300 text-blue-600 focus:ring-blue-500"
              />
              {t('showOnlyFavorites')}
            </label>
          </div>
        </div>
        
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent text-blue-600 motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
            <p className="mt-4 text-neutral-600">{t('loading')}</p>
          </div>
        ) : error ? (
          <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-center">
            <p className="text-red-700">{error}</p>
          </div>
        ) : summaries.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-neutral-200 p-8">
            <p className="text-neutral-600">{favoriteOnly ? t('noFavoriteSummaries') : t('noSummaries')}</p>
            <Link href="/" className="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              {t('createSummary')}
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {summaries.map(summary => (
              <div key={summary.id} className="bg-white rounded-xl shadow-sm border border-neutral-200 p-6 flex flex-col">
                <div className="flex justify-between items-start mb-3">
                  <Link href={`/summary/${summary.id}`} className="hover:text-blue-600">
                    <h2 className="text-lg font-medium text-neutral-900 line-clamp-2">
                      {summary.video_title}
                    </h2>
                  </Link>
                  <button 
                    onClick={() => handleToggleFavorite(summary.id)}
                    className="text-xl text-yellow-500 hover:text-yellow-600"
                    aria-label={summary.is_favorite ? t('unfavorite') : t('favorite')}
                  >
                    {summary.is_favorite ? '★' : '☆'}
                  </button>
                </div>
                
                <div className="flex items-center gap-2 mb-3 text-xs text-neutral-500">
                  <span className="px-2 py-1 bg-neutral-100 rounded-full">{summary.summary_type}</span>
                  <span className="px-2 py-1 bg-neutral-100 rounded-full">{summary.language}</span>
                  <span>{new Date(summary.created_at).toLocaleDateString()}</span>
                </div>
                
                <p className="text-neutral-600 text-sm mb-4 line-clamp-3">
                  {summary.summary_text.substring(0, 150)}...
                </p>
                
                <div className="mt-auto pt-4 flex justify-between">
                  <Link 
                    href={`/summary/${summary.id}`}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    {t('viewDetails')}
                  </Link>
                  <button
                    onClick={() => handleDelete(summary.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    {t('delete')}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
} 