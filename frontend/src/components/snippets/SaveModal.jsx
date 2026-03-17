import { motion, AnimatePresence } from 'framer-motion';
import { useUIStore, useEditorStore, useSnippetsStore, useAuthStore } from '../../store';
import { X, Save, Globe, Lock, Eye } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';

export default function SaveModal() {
  const { showSaveModal, closeSaveModal } = useUIStore();
  const { code, language } = useEditorStore();
  const { createSnippet } = useSnippetsStore();
  const [form, setForm] = useState({
    title: '', description: '', visibility: 'private', tags: '',
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) { toast.error('Title is required'); return; }

    setSaving(true);
    try {
      await createSnippet({
        title: form.title,
        description: form.description,
        code,
        language,
        visibility: form.visibility,
        tags: form.tags ? form.tags.split(',').map(t => t.trim()) : [],
      });
      toast.success('Snippet saved! 🎉');
      closeSaveModal();
      setForm({ title: '', description: '', visibility: 'private', tags: '' });
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!showSaveModal) return null;

  const visibilityOptions = [
    { value: 'private', label: 'Private', icon: Lock, desc: 'Only you can see' },
    { value: 'unlisted', label: 'Unlisted', icon: Eye, desc: 'Anyone with link' },
    { value: 'public', label: 'Public', icon: Globe, desc: 'Visible to everyone' },
  ];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={(e) => e.target === e.currentTarget && closeSaveModal()}
      >
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative w-full max-w-md rounded-2xl glass border border-slate-600/30 shadow-2xl overflow-hidden"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500" />

          <div className="p-6">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                  <Save size={20} className="text-white" />
                </div>
                <h2 className="text-xl font-bold text-white">Save Snippet</h2>
              </div>
              <button
                onClick={closeSaveModal}
                className="p-2 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSave} className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1.5">Title *</label>
                <input
                  type="text"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="My awesome snippet"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700/50 text-slate-200 text-sm placeholder-slate-500 outline-none focus:border-indigo-500/50 transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-sm text-slate-400 mb-1.5">Description</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder="What does this code do?"
                  rows={2}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700/50 text-slate-200 text-sm placeholder-slate-500 outline-none focus:border-indigo-500/50 transition-all resize-none"
                />
              </div>

              <div>
                <label className="block text-sm text-slate-400 mb-1.5">Tags</label>
                <input
                  type="text"
                  value={form.tags}
                  onChange={(e) => setForm({ ...form, tags: e.target.value })}
                  placeholder="algorithm, sorting, python (comma-separated)"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700/50 text-slate-200 text-sm placeholder-slate-500 outline-none focus:border-indigo-500/50 transition-all"
                />
              </div>

              <div>
                <label className="block text-sm text-slate-400 mb-2">Visibility</label>
                <div className="grid grid-cols-3 gap-2">
                  {visibilityOptions.map(({ value, label, icon: Icon, desc }) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => setForm({ ...form, visibility: value })}
                      className={`p-3 rounded-xl border text-center transition-all ${
                        form.visibility === value
                          ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-300'
                          : 'bg-slate-800/50 border-slate-700/30 text-slate-400 hover:border-slate-600'
                      }`}
                    >
                      <Icon size={16} className="mx-auto mb-1" />
                      <div className="text-xs font-medium">{label}</div>
                      <div className="text-[10px] text-slate-500 mt-0.5">{desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <div className="px-3 py-1 rounded-lg bg-slate-800/80 text-xs text-slate-400 border border-slate-700/30">
                  {language}
                </div>
                <div className="px-3 py-1 rounded-lg bg-slate-800/80 text-xs text-slate-400 border border-slate-700/30">
                  {code?.length || 0} chars
                </div>
              </div>

              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                type="submit"
                disabled={saving}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-sm shadow-lg shadow-emerald-500/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                {saving ? (
                  <div className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                ) : (
                  <>
                    <Save size={16} />
                    Save Snippet
                  </>
                )}
              </motion.button>
            </form>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
