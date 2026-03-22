/**
 * 认证状态管理 (Zustand)
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '../api/auth';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      // 状态
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          console.log('调用登录API...');
          const response = await authApi.login(credentials);
          console.log('登录API响应:', response);
          
          // response 包含 { code, data: { access_token, user } }
          console.log('response.data:', response.data);
          const { access_token, user } = response.data;
          console.log('解构结果:', { access_token: access_token?.substring(0, 10), user });
          
          // 保存token
          localStorage.setItem('access_token', access_token);
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
          
          return true;
        } catch (error) {
          console.error('登录错误:', error);
          set({
            error: error.message,
            isLoading: false,
            isAuthenticated: false,
          });
          return false;
        }
      },

      logout: () => {
        localStorage.removeItem('access_token');
        set({
          user: null,
          isAuthenticated: false,
          error: null,
        });
      },

      fetchUser: async () => {
        try {
          const response = await authApi.getMe();
          // response.data 已经是 user 数据
          set({
            user: response.data,
            isAuthenticated: true,
          });
        } catch (error) {
          // Token无效，清除登录状态
          console.log('fetchUser error:', error);
          // 清除 persist 存储的状态
          localStorage.removeItem('auth-storage');
          get().logout();
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage', // localStorage key
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
