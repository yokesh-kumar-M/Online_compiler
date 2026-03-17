import { motion, AnimatePresence } from 'framer-motion';
import { useUIStore, useEditorStore } from '../../store';
import { X, Share2, Copy, Check, Link, ExternalLink } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';

export default function ShareModal() {
  const { showShareModal, closeShareModal } = useUIStore();
  const { code, language } = useEditorStore();
  const [copied, setCopied] = useState(false);

  const shareUrl = window.location.origin;

  const copyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    toast.success('Code copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const copyLink = () => {
    navigator.clipboard.writeText(shareUrl);
    toast.success('Link copied!');
  };

  if (!showShareModal) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={(e) => e.target === e.currentTarget && closeShareModal()}
      >
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative w-full max-w-md rounded-2xl glass border border-slate-600/30 shadow-2xl overflow-hidden"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500" />

          <div className="p-6">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                  <Share2 size={20} className="text-white" />
                </div>
                <h2 className="text-xl font-bold text-white">Share Code</h2>
              </div>
              <button
                onClick={closeShareModal}
                className="p-2 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-4">
              {/* Code preview */}
              <div className="rounded-xl bg-slate-900/80 border border-slate-700/30 overflow-hidden">
                <div className="flex items-center justify-between px-3 py-2 border-b border-slate-700/30">
                  <span className="text-xs text-slate-400">{language}</span>
                  <span className="text-xs text-slate-500">{code?.length || 0} chars</span>
                </div>
                <pre className="p-3 text-xs text-slate-300 max-h-32 overflow-y-auto font-mono">
                  {code?.substring(0, 500)}
                  {code?.length > 500 && '...'}
                </pre>
              </div>

              {/* Copy Code */}
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={copyCode}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-sm shadow-lg transition-all"
              >
                {copied ? <Check size={16} /> : <Copy size={16} />}
                {copied ? 'Copied!' : 'Copy Code'}
              </motion.button>

              {/* Share link */}
              <div className="flex items-center gap-2">
                <div className="flex-1 px-3 py-2 rounded-lg bg-slate-800/80 border border-slate-700/50 text-xs text-slate-400 truncate">
                  {shareUrl}
                </div>
                <button
                  onClick={copyLink}
                  className="p-2 rounded-lg bg-slate-800 border border-slate-700/50 text-slate-400 hover:text-white transition-colors"
                >
                  <Link size={14} />
                </button>
              </div>

              <p className="text-xs text-slate-500 text-center">
                💡 Save as a public snippet to get a shareable link
              </p>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
