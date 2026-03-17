import { motion, AnimatePresence } from 'framer-motion';
import { useUIStore, useSnippetsStore, useEditorStore, useAuthStore } from '../../store';
import {
  X, FolderOpen, Star, GitFork, Trash2, Code2, Clock,
  Eye, Lock, Globe, Loader2, Search, ChevronRight
} from 'lucide-react';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';

export default function SnippetsPanel() {
  const { showSnippetsPanel, closeSnippetsPanel } = useUIStore();
  const { snippets, fetchSnippets, deleteSnippet, starSnippet, forkSnippet, loading } = useSnippetsStore();
  const { setCode, setLanguage } = useEditorStore();
  const { isAuthenticated } = useAuthStore();
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (showSnippetsPanel) {
      fetchSnippets();
    }
  }, [showSnippetsPanel]);

  const loadSnippet = (snippet) => {
    setCode(snippet.code);
    if (snippet.language) setLanguage(snippet.language);
    closeSnippetsPanel();
    toast.success(`Loaded: ${snippet.title}`);
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!confirm('Delete this snippet?')) return;
    try {
      await deleteSnippet(id);
      toast.success('Snippet deleted');
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleStar = async (e, id) => {
    e.stopPropagation();
    try {
      const result = await starSnippet(id);
      toast.success(result.status === 'starred' ? '⭐ Starred!' : 'Unstarred');
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleFork = async (e, id) => {
    e.stopPropagation();
    try {
      const forked = await forkSnippet(id);
      setCode(forked.code);
      if (forked.language) setLanguage(forked.language);
      closeSnippetsPanel();
      toast.success('Snippet forked!');
    } catch (err) {
      toast.error(err.message);
    }
  };

  const filteredSnippets = snippets.filter(s =>
    s.title?.toLowerCase().includes(search.toLowerCase()) ||
    s.language?.toLowerCase().includes(search.toLowerCase())
  );

  const visibilityIcon = {
    private: Lock,
    unlisted: Eye,
    public: Globe,
  };

  if (!showSnippetsPanel) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex justify-end"
        onClick={(e) => e.target === e.currentTarget && closeSnippetsPanel()}
      >
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />

        <motion.div
          initial={{ x: 400 }}
          animate={{ x: 0 }}
          exit={{ x: 400 }}
          transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          className="relative w-full max-w-md h-full glass border-l border-slate-700/50 shadow-2xl flex flex-col"
        >
          {/* Header */}
          <div className="p-4 border-b border-slate-700/50">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
                  <FolderOpen size={18} className="text-white" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">My Snippets</h2>
                  <p className="text-xs text-slate-400">{snippets.length} snippets</p>
                </div>
              </div>
              <button
                onClick={closeSnippetsPanel}
                className="p-2 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Search */}
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search snippets..."
                className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-800/80 border border-slate-700/50 text-slate-200 text-sm placeholder-slate-500 outline-none focus:border-indigo-500/50 transition-all"
              />
            </div>
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 size={24} className="text-indigo-500 animate-spin" />
              </div>
            ) : !isAuthenticated ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Lock size={32} className="text-slate-600 mb-3" />
                <p className="text-slate-400 text-sm">Sign in to view your snippets</p>
              </div>
            ) : filteredSnippets.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Code2 size={32} className="text-slate-600 mb-3" />
                <p className="text-slate-400 text-sm">
                  {search ? 'No matching snippets' : 'No snippets yet'}
                </p>
                <p className="text-slate-600 text-xs mt-1">
                  Save your code using the Save button
                </p>
              </div>
            ) : (
              filteredSnippets.map((snippet, idx) => {
                const VisIcon = visibilityIcon[snippet.visibility] || Lock;
                return (
                  <motion.div
                    key={snippet.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.03 }}
                    whileHover={{ scale: 1.01, x: 2 }}
                    onClick={() => loadSnippet(snippet)}
                    className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/30 hover:border-indigo-500/30 cursor-pointer transition-all group"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors truncate flex-1">
                        {snippet.title}
                      </h3>
                      <div className="flex items-center gap-1 ml-2 flex-shrink-0">
                        <VisIcon size={12} className="text-slate-500" />
                      </div>
                    </div>

                    {snippet.description && (
                      <p className="text-xs text-slate-500 mb-2 line-clamp-2">
                        {snippet.description}
                      </p>
                    )}

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] px-2 py-0.5 rounded-md bg-slate-700/50 text-slate-400">
                          {snippet.language}
                        </span>
                        <span className="text-[10px] text-slate-600 flex items-center gap-1">
                          <Clock size={10} />
                          {new Date(snippet.updated_at).toLocaleDateString()}
                        </span>
                      </div>

                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        {isAuthenticated && (
                          <>
                            <button
                              onClick={(e) => handleStar(e, snippet.id)}
                              className={`p-1 rounded hover:bg-slate-700 transition-colors ${
                                snippet.is_starred ? 'text-amber-400' : 'text-slate-500 hover:text-amber-400'
                              }`}
                              title="Star"
                            >
                              <Star size={12} className={snippet.is_starred ? 'fill-current' : ''} />
                            </button>
                            <button
                              onClick={(e) => handleFork(e, snippet.id)}
                              className="p-1 rounded hover:bg-slate-700 text-slate-500 hover:text-indigo-400 transition-colors"
                              title="Fork"
                            >
                              <GitFork size={12} />
                            </button>
                            <button
                              onClick={(e) => handleDelete(e, snippet.id)}
                              className="p-1 rounded hover:bg-slate-700 text-slate-500 hover:text-red-400 transition-colors"
                              title="Delete"
                            >
                              <Trash2 size={12} />
                            </button>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Stars count */}
                    {snippet.stars_count > 0 && (
                      <div className="flex items-center gap-1 mt-1.5 text-[10px] text-amber-500/60">
                        <Star size={10} className="fill-current" />
                        {snippet.stars_count}
                      </div>
                    )}
                  </motion.div>
                );
              })
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
