import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { LanguageProvider } from '@/contexts/LanguageContext';
import { AuthProvider } from '@/contexts/AuthContext';
import dynamic from 'next/dynamic';

// 使用相对路径导入Navbar组件
const Navbar = dynamic(() => import('../components/Navbar'), { ssr: false });

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'YouTube Video Summarizer',
  description: 'Get AI-powered summaries of YouTube videos',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <LanguageProvider>
            <Navbar />
            {children}
          </LanguageProvider>
        </AuthProvider>
      </body>
    </html>
  );
} 