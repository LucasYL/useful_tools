'use client';
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

// API基础URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://useful-tools.onrender.com';

// 用户类型定义
interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

// 认证上下文接口
interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

// 创建上下文
const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  loading: false,
  error: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  isAuthenticated: false,
});

// 认证提供者组件
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // 初始化 - 从本地存储加载认证状态
  useEffect(() => {
    const loadStoredAuth = async () => {
      try {
        const storedToken = localStorage.getItem('auth_token');
        
        if (storedToken) {
          // 验证令牌并获取用户信息
          const userInfo = await fetchUserInfo(storedToken);
          setUser(userInfo);
          setToken(storedToken);
          setIsAuthenticated(true);
        }
      } catch (err) {
        console.error('Failed to load auth state:', err);
        // 清除无效令牌
        localStorage.removeItem('auth_token');
      } finally {
        setLoading(false);
      }
    };

    loadStoredAuth();
  }, []);

  // 登录方法
  const login = async (username: string, password: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // 构造表单数据
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      // 发送登录请求
      const response = await axios.post(`${API_BASE_URL}/auth/token`, formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      const { access_token } = response.data;
      
      // 保存令牌到本地存储
      localStorage.setItem('auth_token', access_token);
      
      // 获取用户信息
      const userInfo = await fetchUserInfo(access_token);
      
      // 更新状态
      setToken(access_token);
      setUser(userInfo);
      setIsAuthenticated(true);
    } catch (err: any) {
      console.error('Login failed:', err);
      setError(err.response?.data?.detail || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  // 注册方法
  const register = async (username: string, email: string, password: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // 发送注册请求
      await axios.post(`${API_BASE_URL}/auth/register`, {
        username,
        email,
        password,
      });
      
      // 注册成功后自动登录
      await login(username, password);
    } catch (err: any) {
      console.error('Registration failed:', err);
      setError(err.response?.data?.detail || '注册失败，请稍后再试');
    } finally {
      setLoading(false);
    }
  };

  // 登出方法
  const logout = () => {
    // 清除本地存储和状态
    localStorage.removeItem('auth_token');
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
  };

  // 获取用户信息
  const fetchUserInfo = async (authToken: string): Promise<User> => {
    const response = await axios.get(`${API_BASE_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });
    return response.data;
  };

  // 提供上下文值
  const contextValue: AuthContextType = {
    user,
    token,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// 自定义钩子以便在组件中使用
export function useAuth() {
  return useContext(AuthContext);
} 