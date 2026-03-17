import { motion } from 'framer-motion';
import {
  Play, Square, ChevronDown, CheckCircle, AlignLeft, Save,
  Share2, Eraser, Keyboard, BookOpen, FolderOpen, Loader2
} from 'lucide-react';
import { useEditorStore, useUIStore, useAuthStore } from '../../store';
import { LANGUAGE_CONFIG } from '../../utils/constants';
import { useState, useRef, useEffect } from 'react';
import toast from 'react-hot-toast';

export default function Toolbar() {
  const { language, setLanguage, setCode, isRunning, runCode, clearOutput } = useEditorStore();
  const { openExamplesModal, openSaveModal, toggleSnippetsPanel, openShareModal, openAuthModal } = useUIStore();
  const { isAuthenticated } = useAuthStore();
  const [showLangDropdown, setShowLangDropdown] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowLangDropdown(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleRun = async () => {
    try {
      await runCode();
      toast.success('Code executed!');
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleLanguageChange = (lang) => {
    setLanguage(lang);
    const config = LANGUAGE_CONFIG[lang];
    if (config?.template) {
      setCode(config.template);
    }
    setShowLangDropdown(false);
  };

  const handleSave = () => {
    if (!isAuthenticated) {
      openAuthModal('login');
      toast('Sign in to save snippets', { icon: '🔒' });
      return;
    }
    openSaveModal();
  };

  const handleFormat = () => {
    toast.success('Code formatted');
  };

  const currentLang = LANGUAGE_CONFIG[language];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex items-center gap-2 px-3 py-2 bg-slate-900/90 border-b border-slate-700/50 overflow-x-auto"
    >
      {/* Run Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleRun}
        disabled={isRunning}
        className={`flex items-center gap-2 px-4 py-2 rounded-xl font-semibold text-sm text-white shadow-lg transition-all ${
          isRunning
            ? 'bg-amber-600 shadow-amber-500/25 cursor-wait'
            : 'bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 shadow-emerald-500/25 glow-green'
        }`}
      >
        {isRunning ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            Running...
          </>
        ) : (
          <>
            <Play size={16} className="fill-current" />
            Run
          </>
        )}
      </motion.button>

      <div className="w-px h-6 bg-slate-700/50" />

      {/* Language Selector */}
      <div className="relative" ref={dropdownRef}>
        <motion.button
          whileHover={{ scale: 1.02 }}
          onClick={() => setShowLangDropdown(!showLangDropdown)}
          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-800 border border-slate-700/50 hover:border-indigo-500/50 text-sm transition-all min-w-36"
        >
          <span className="text-lg">{currentLang?.icon}</span>
          <span className="text-slate-200">{currentLang?.name}</span>
          <ChevronDown size={14} className={`text-slate-400 transition-transform ml-auto ${showLangDropdown ? 'rotate-180' : ''}`} />
        </motion.button>

        {showLangDropdown && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full mt-2 left-0 w-56 rounded-xl glass border border-slate-600/50 shadow-2xl z-50 overflow-hidden"
          >
            {Object.entries(LANGUAGE_CONFIG).map(([key, config]) => (
              <button
                key={key}
                onClick={() => handleLanguageChange(key)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-all ${
                  language === key
                    ? 'bg-indigo-500/20 text-indigo-300'
                    : 'text-slate-300 hover:bg-slate-700/50'
                }`}
              >
                <span className="text-lg">{config.icon}</span>
                <span>{config.name}</span>
                {language === key && (
                  <CheckCircle size={14} className="ml-auto text-indigo-400" />
                )}
              </button>
            ))}
          </motion.div>
        )}
      </div>

      <div className="w-px h-6 bg-slate-700/50" />

      {/* Action Buttons */}
      <ToolbarButton icon={AlignLeft} label="Format" onClick={handleFormat} shortcut="Ctrl+Shift+F" />
      <ToolbarButton icon={BookOpen} label="Examples" onClick={openExamplesModal} />

      <div className="w-px h-6 bg-slate-700/50" />

      <ToolbarButton icon={Save} label="Save" onClick={handleSave} shortcut="Ctrl+S" />
      <ToolbarButton icon={FolderOpen} label="My Snippets" onClick={toggleSnippetsPanel} />
      <ToolbarButton icon={Share2} label="Share" onClick={() => {
        if (!isAuthenticated) { openAuthModal('login'); toast('Sign in to share', { icon: '🔒' }); return; }
        openShareModal();
      }} />

      <div className="flex-1" />

      <ToolbarButton
        icon={Eraser}
        label=""
        onClick={() => {
          setCode(LANGUAGE_CONFIG[language]?.template || '');
          clearOutput();
          toast.success('Editor cleared');
        }}
        title="Clear Editor"
      />
    </motion.div>
  );
}

function ToolbarButton({ icon: Icon, label, onClick, shortcut, title }) {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      title={title || `${label}${shortcut ? ` (${shortcut})` : ''}`}
      className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 text-sm transition-all"
    >
      <Icon size={14} />
      {label && <span className="hidden lg:inline">{label}</span>}
    </motion.button>
  );
}
