import { create } from 'zustand';
import { authAPI, compilerAPI, snippetsAPI } from '../api/client';

// ─── Auth Store ──────────────────────────────────────────────
export const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null,

  initialize: async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const { data } = await authAPI.profile();
        set({ user: data, isAuthenticated: true });
      } catch {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
  },

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const { data } = await authAPI.login({ email, password });
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);
      set({ user: data.user, isAuthenticated: true, loading: false });
      return data;
    } catch (err) {
      const msg = err.response?.data?.detail ||
        err.response?.data?.non_field_errors?.[0] ||
        JSON.stringify(err.response?.data) ||
        'Login failed';
      set({ error: msg, loading: false });
      throw new Error(msg);
    }
  },

  register: async (formData) => {
    set({ loading: true, error: null });
    try {
      const { data } = await authAPI.register(formData);
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);
      set({ user: data.user, isAuthenticated: true, loading: false });
      return data;
    } catch (err) {
      const errors = err.response?.data;
      let msg = 'Registration failed';
      if (errors) {
        msg = Object.entries(errors)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
          .join('\n');
      }
      set({ error: msg, loading: false });
      throw new Error(msg);
    }
  },

  logout: async () => {
    const refresh = localStorage.getItem('refresh_token');
    try {
      if (refresh) await authAPI.logout(refresh);
    } catch {}
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false });
  },

  clearError: () => set({ error: null }),
}));

// ─── Editor Store ────────────────────────────────────────────
export const useEditorStore = create((set, get) => ({
  code: '# Welcome to CodeForge! 🚀\nprint("Hello, World!")\n\nfor i in range(5):\n    print(f"  {i+1}. Python is awesome!")\n',
  language: 'python',
  stdin: '',
  output: null,
  isRunning: false,
  executionTime: null,
  executionId: null,
  activeOutputTab: 'output',
  theme: 'vs-dark',

  setCode: (code) => set({ code }),
  setLanguage: (language) => set({ language }),
  setStdin: (stdin) => set({ stdin }),
  setActiveOutputTab: (tab) => set({ activeOutputTab: tab }),

  runCode: async () => {
    const { code, language, stdin } = get();
    if (!code.trim()) return;

    set({ isRunning: true, output: null, executionTime: null, activeOutputTab: 'output' });

    try {
      const { data } = await compilerAPI.execute({ code, language, stdin });
      set({
        output: {
          success: data.success,
          content: data.success ? (data.output || '✅ Executed successfully (no output)') : (data.error || 'Unknown error'),
          executionTime: data.execution_time_ms,
        },
        executionTime: data.execution_time_ms,
        executionId: data.execution_id,
        isRunning: false,
      });
      return data;
    } catch (err) {
      const errorMsg = err.response?.status === 429
        ? '⚠️ Rate limit exceeded. Please wait before trying again.'
        : err.response?.data?.error || err.message || 'Execution failed';
      set({
        output: { success: false, content: errorMsg },
        isRunning: false,
      });
      throw new Error(errorMsg);
    }
  },

  clearOutput: () => set({ output: null, executionTime: null }),
}));

// ─── Snippets Store ──────────────────────────────────────────
export const useSnippetsStore = create((set, get) => ({
  snippets: [],
  currentSnippet: null,
  loading: false,
  error: null,

  fetchSnippets: async (params = {}) => {
    set({ loading: true });
    try {
      const { data } = await snippetsAPI.list(params);
      set({ snippets: data.results || data, loading: false });
    } catch (err) {
      set({ error: 'Failed to load snippets', loading: false });
    }
  },

  createSnippet: async (snippetData) => {
    try {
      const { data } = await snippetsAPI.create(snippetData);
      set((state) => ({ snippets: [data, ...state.snippets], currentSnippet: data }));
      return data;
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to save snippet');
    }
  },

  updateSnippet: async (id, snippetData) => {
    try {
      const { data } = await snippetsAPI.update(id, snippetData);
      set((state) => ({
        snippets: state.snippets.map((s) => (s.id === id ? data : s)),
        currentSnippet: data,
      }));
      return data;
    } catch (err) {
      throw new Error('Failed to update snippet');
    }
  },

  deleteSnippet: async (id) => {
    try {
      await snippetsAPI.delete(id);
      set((state) => ({
        snippets: state.snippets.filter((s) => s.id !== id),
        currentSnippet: state.currentSnippet?.id === id ? null : state.currentSnippet,
      }));
    } catch (err) {
      throw new Error('Failed to delete snippet');
    }
  },

  starSnippet: async (id) => {
    try {
      const { data } = await snippetsAPI.star(id);
      set((state) => ({
        snippets: state.snippets.map((s) =>
          s.id === id
            ? {
                ...s,
                is_starred: data.status === 'starred',
                stars_count: s.stars_count + (data.status === 'starred' ? 1 : -1),
              }
            : s
        ),
      }));
      return data;
    } catch (err) {
      throw new Error('Failed to star snippet');
    }
  },

  forkSnippet: async (id) => {
    try {
      const { data } = await snippetsAPI.fork(id);
      set((state) => ({ snippets: [data, ...state.snippets] }));
      return data;
    } catch (err) {
      throw new Error('Failed to fork snippet');
    }
  },
}));

// ─── UI Store ────────────────────────────────────────────────
export const useUIStore = create((set) => ({
  showAuthModal: false,
  authModalMode: 'login',
  showExamplesModal: false,
  showSnippetsPanel: false,
  showSaveModal: false,
  showSettingsModal: false,
  showShareModal: false,
  sidebarCollapsed: false,

  openAuthModal: (mode = 'login') => set({ showAuthModal: true, authModalMode: mode }),
  closeAuthModal: () => set({ showAuthModal: false }),
  toggleAuthMode: () =>
    set((s) => ({ authModalMode: s.authModalMode === 'login' ? 'register' : 'login' })),

  openExamplesModal: () => set({ showExamplesModal: true }),
  closeExamplesModal: () => set({ showExamplesModal: false }),

  toggleSnippetsPanel: () => set((s) => ({ showSnippetsPanel: !s.showSnippetsPanel })),
  closeSnippetsPanel: () => set({ showSnippetsPanel: false }),

  openSaveModal: () => set({ showSaveModal: true }),
  closeSaveModal: () => set({ showSaveModal: false }),

  openSettingsModal: () => set({ showSettingsModal: true }),
  closeSettingsModal: () => set({ showSettingsModal: false }),

  openShareModal: () => set({ showShareModal: true }),
  closeShareModal: () => set({ showShareModal: false }),

  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
}));
