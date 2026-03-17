import { useEffect, useCallback, useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { motion } from 'framer-motion';
import Navbar from './components/layout/Navbar';
import Toolbar from './components/layout/Toolbar';
import StatusBar from './components/layout/StatusBar';
import CodeEditor from './components/editor/CodeEditor';
import OutputPanel from './components/editor/OutputPanel';
import AuthModal from './components/auth/AuthModal';
import ExamplesModal from './components/common/ExamplesModal';
import SaveModal from './components/snippets/SaveModal';
import SnippetsPanel from './components/snippets/SnippetsPanel';
import ShareModal from './components/common/ShareModal';
import SettingsModal from './components/common/SettingsModal';
import { useAuthStore, useEditorStore, useUIStore } from './store';

export default function App() {
  const { initialize } = useAuthStore();
  const { runCode } = useEditorStore();
  const { openSaveModal } = useUIStore();

  useEffect(() => {
    initialize();
  }, []);

  // Global keyboard shortcuts
  const handleKeyDown = useCallback((e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      runCode();
    }
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      openSaveModal();
    }
    if (e.key === 'F5') {
      e.preventDefault();
      runCode();
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'F' || e.key === 'f')) {
      e.preventDefault();
      if (window.__monacoEditor) {
        window.__monacoEditor.getAction('editor.action.formatDocument')?.run();
      }
    }
  }, [runCode, openSaveModal]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-slate-100 overflow-hidden noise-bg relative">
      {/* Ambient background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/4 w-[800px] h-[800px] bg-indigo-500/[0.03] rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -right-1/4 w-[600px] h-[600px] bg-purple-500/[0.03] rounded-full blur-3xl" />
        <div className="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-emerald-500/[0.02] rounded-full blur-3xl" />
      </div>

      {/* Main Layout */}
      <div className="relative z-10 flex flex-col h-full">
        <Navbar />
        <Toolbar />

        {/* Editor + Output */}
        <div className="flex-1 flex overflow-hidden">
          {/* Editor Section */}
          <motion.div
            className="flex-1 flex flex-col min-w-0"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <CodeEditor />
          </motion.div>

          {/* Resize Handle */}
          <div className="w-1 bg-slate-800/50 hover:bg-indigo-500/50 cursor-col-resize transition-colors flex-shrink-0" />

          {/* Output Panel */}
          <motion.div
            className="w-[38%] min-w-[280px] flex-shrink-0 hidden md:flex"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <OutputPanel />
          </motion.div>
        </div>

        {/* Mobile Output Toggle */}
        <MobileOutputToggle />

        <StatusBar />
      </div>

      {/* Modals */}
      <AuthModal />
      <ExamplesModal />
      <SaveModal />
      <SnippetsPanel />
      <ShareModal />
      <SettingsModal />

      {/* Toast */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#1e293b',
            color: '#f1f5f9',
            border: '1px solid rgba(71, 85, 105, 0.5)',
            borderRadius: '12px',
            fontSize: '13px',
            backdropFilter: 'blur(16px)',
          },
          success: {
            iconTheme: { primary: '#10b981', secondary: '#f1f5f9' },
          },
          error: {
            iconTheme: { primary: '#ef4444', secondary: '#f1f5f9' },
          },
        }}
      />
    </div>
  );
}

function MobileOutputToggle() {
  const { output, isRunning } = useEditorStore();
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="md:hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full py-2 bg-slate-900 border-t border-slate-700/50 text-xs text-slate-400 flex items-center justify-center gap-2"
      >
        {isRunning ? (
          <>
            <div className="w-3 h-3 rounded-full border border-slate-600 border-t-indigo-500 animate-spin" />
            Running...
          </>
        ) : (
          <>
            {expanded ? '▼' : '▲'} Output {output?.success !== undefined && (output.success ? '✅' : '❌')}
          </>
        )}
      </button>
      {expanded && (
        <div className="h-48 border-t border-slate-700/50">
          <OutputPanel />
        </div>
      )}
    </div>
  );
}
