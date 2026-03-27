/**
 * 全局 Store 入口
 * 使用 Zustand 管理跨模块共享状态
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// 用户状态
export const useUserStore = create(
  persist(
    (set, get) => ({
      // 状态
      user: null,
      isAuthenticated: false,
      
      // Actions
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, isAuthenticated: false });
      },
      
      // Getters
      getUserId: () => get().user?.id,
      getUserName: () => get().user?.name,
      hasRole: (role) => get().user?.roles?.includes(role),
    }),
    {
      name: 'user-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);

// 应用状态
export const useAppStore = create((set, get) => ({
  // 状态
  sidebarCollapsed: false,
  theme: 'light',
  
  // Actions
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setTheme: (theme) => set({ theme }),
}));
