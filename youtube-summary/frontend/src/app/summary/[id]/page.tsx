'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { VideoPlayer } from '@/components/VideoPlayer';
import { SummaryDisplay } from '@/components/SummaryDisplay';

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
  video_youtube_id: string;
}

export default function SummaryDetail() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const params = useParams();
  const summaryId = params?.id?.toString();
  const { isAuthenticated, token } = useAuth();
  const router = useRouter();
  const { t } = useLanguage();

  // 加载摘要数据
  useEffect(() => {
    const fetchSummary = async () => {
      if (!isAuthenticated || !token) {
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`${API_BASE_URL}/api/summaries/${summaryId}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        console.log('获取到摘要数据:', response.data);
        setSummary(response.data);
      } catch (err: any) {
        console.error('Failed to fetch summary:', err);
        setError(err.response?.data?.detail || t('failedToLoadSummary'));
      } finally {
        setLoading(false);
      }
    };

    if (summaryId) {
      fetchSummary();
    }
  }, [isAuthenticated, token, summaryId]);

  // 处理收藏切换
  const handleToggleFavorite = async () => {
    if (!token || !summary) return;
    
    try {
      const response = await axios.patch(
        `${API_BASE_URL}/api/summaries/${summary.id}/favorite`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      setSummary(prev => prev ? { ...prev, is_favorite: response.data.is_favorite } : null);
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  // 处理删除摘要
  const handleDelete = async () => {
    if (!token || !summary) return;
    
    if (window.confirm(t('confirmDelete'))) {
      try {
        await axios.delete(`${API_BASE_URL}/api/summaries/${summary.id}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        router.push('/history');
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
          <p className="mb-6 text-neutral-600">{t('loginToViewSummary')}</p>
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

  // 加载状态
  if (loading) {
    return (
      <main className="min-h-screen bg-neutral-50 p-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent text-blue-600 motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
            <p className="mt-4 text-neutral-600">{t('loading')}</p>
          </div>
        </div>
      </main>
    );
  }

  // 错误状态
  if (error || !summary) {
    return (
      <main className="min-h-screen bg-neutral-50 p-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-semibold">{t('summaryDetail')}</h1>
            <Link href="/history" className="text-sm text-neutral-600 hover:text-neutral-900">
              &larr; {t('backToHistory')}
            </Link>
          </div>
          
          <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-center">
            <p className="text-red-700">{error || t('summaryNotFound')}</p>
            <Link href="/history" className="mt-4 inline-block text-blue-600 hover:text-blue-800">
              {t('backToHistory')}
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
          <h1 className="text-2xl font-semibold truncate max-w-xl">{summary.video_title}</h1>
          <div className="flex gap-4">
            <button 
              onClick={handleToggleFavorite}
              className="flex items-center text-sm px-4 py-2 border border-neutral-300 rounded-lg hover:bg-neutral-100 transition-colors"
            >
              <span className="mr-2 text-yellow-500">{summary.is_favorite ? '★' : '☆'}</span>
              {summary.is_favorite ? t('unfavorite') : t('favorite')}
            </button>
            <button 
              onClick={handleDelete}
              className="flex items-center text-sm px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
            >
              <span className="mr-2">🗑️</span>
              {t('delete')}
            </button>
            <Link href="/history" className="flex items-center text-sm px-4 py-2 border border-neutral-300 rounded-lg hover:bg-neutral-100 transition-colors">
              &larr; {t('backToHistory')}
            </Link>
          </div>
        </div>
        
        <div className="flex items-center gap-2 mb-6 text-sm text-neutral-500">
          <span className="px-2 py-1 bg-neutral-100 rounded-full">{summary.summary_type}</span>
          <span className="px-2 py-1 bg-neutral-100 rounded-full">{summary.language}</span>
          <span>{new Date(summary.created_at).toLocaleString()}</span>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧 - 视频 */}
          <div>
            <VideoPlayer 
              videoId={summary.video_youtube_id} 
              onTimeUpdate={() => {}}
            />
          </div>
          
          {/* 右侧 - 摘要内容 */}
          <div className="bg-white rounded-xl shadow-sm border border-neutral-200 p-6">
            <h2 className="text-xl font-medium mb-4">{t('summaryContent')}</h2>
            <div className="prose max-w-none">
              <SummaryDisplay
                summary={summary.summary_text}
                title={summary.video_title}
                summaryType={summary.summary_type}
                videoId={summary.video_youtube_id}
                onSeek={() => {}}
              />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
} 