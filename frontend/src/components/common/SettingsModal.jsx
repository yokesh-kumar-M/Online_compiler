import { motion, AnimatePresence } from 'framer-motion';
import { useUIStore } from '../../store';
import { X, Settings, Keyboard, Info, Heart, ExternalLink, Github } from 'lucide-react';
import { KEYBOARD_SHORTCUTS } from '../../utils/constants';

export default function SettingsModal() {
  const { showSettingsModal, closeSettingsModal } = useUIStore();

  if (!showSettingsModal) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={(e) => e.target === e.currentTarget && closeSettingsModal()}
      >
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative w-full max-w-lg rounded-2xl glass border border-slate-600/30 shadow-2xl overflow-hidden"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-slate-500 via-indigo-500 to-slate-500" />

          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center">
                  <Settings size={20} className="text-white" />
                </div>
                <h2 className="text-xl font-bold text-white">Settings & Info</h2>
              </div>
              <button
                onClick={closeSettingsModal}
                className="p-2 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Keyboard Shortcuts */}
            <div className="mb-6">
              <h3 className="flex items-center gap-2 text-sm font-semibold text-white mb-3">
                <Keyboard size={16} className="text-indigo-400" />
                Keyboard Shortcuts
              </h3>
              <div className="grid grid-cols-2 gap-2">
                {KEYBOARD_SHORTCUTS.map((shortcut, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.03 }}
                    className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/30"
                  >
                    <span className="text-xs text-slate-400">{shortcut.action}</span>
                    <kbd className="px-2 py-0.5 rounded bg-slate-700 text-[10px] text-slate-300 font-mono border border-slate-600">
                      {shortcut.keys}
                    </kbd>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* About */}
            <div className="mb-4">
              <h3 className="flex items-center gap-2 text-sm font-semibold text-white mb-3">
                <Info size={16} className="text-blue-400" />
                About CodeForge
              </h3>
              <div className="space-y-2 text-xs text-slate-400">
                <p>Enterprise-grade online code compilation platform built with Django, React, and microservices architecture.</p>
                <div className="flex flex-wrap gap-2 mt-2">
                  {['Python', 'JavaScript', 'C', 'C++', 'Java', 'Go'].map((lang) => (
                    <span key={lang} className="px-2 py-1 rounded-lg bg-slate-800/80 border border-slate-700/30 text-slate-300">
                      {lang}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Links */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-700/50">
              <div className="flex items-center gap-2">
                <a
                  href="/api/docs/"
                  target="_blank"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/30 text-xs text-slate-400 hover:text-white hover:border-indigo-500/30 transition-all"
                >
                  <ExternalLink size={12} />
                  API Docs
                </a>
                <a
                  href="https://github.com/yokesh-kumar-M/Online_compiler"
                  target="_blank"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/30 text-xs text-slate-400 hover:text-white hover:border-indigo-500/30 transition-all"
                >
                  <Github size={12} />
                  GitHub
                </a>
              </div>
              <p className="text-xs text-slate-600 flex items-center gap-1">
                Made with <Heart size={10} className="text-red-400 fill-current" /> by Yokesh Kumar
              </p>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
