import { motion, AnimatePresence } from 'framer-motion';
import {
  Terminal, Code2, Play, Menu, LogIn, UserPlus, LogOut,
  User, ChevronDown, Zap, Settings, BookOpen, FolderOpen
} from 'lucide-react';
import { useAuthStore, useUIStore, useEditorStore } from '../../store';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const { openAuthModal, openExamplesModal, toggleSnippetsPanel, openSettingsModal } = useUIStore();
  const { executionTime } = useEditorStore();

  return (
    <motion.nav
      initial={{ y: -60 }}
      animate={{ y: 0 }}
      className="relative z-40 h-14 flex items-center justify-between px-4 glass border-b border-slate-700/50"
    >
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg glow-indigo">
            <Terminal size={18} className="text-white" />
          </div>
          <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-green-400 rounded-full border-2 border-slate-900 animate-pulse" />
        </div>
        <div className="hidden sm:block">
          <h1 className="text-lg font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            CodeForge
          </h1>
          <p className="text-[10px] text-slate-500 -mt-0.5 tracking-wider uppercase">Enterprise</p>
        </div>
      </div>

      {/* Center Actions */}
      <div className="hidden md:flex items-center gap-1">
        <NavButton icon={BookOpen} label="Examples" onClick={openExamplesModal} />
        <NavButton icon={FolderOpen} label="Snippets" onClick={toggleSnippetsPanel} />
        {executionTime && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-800/80 text-xs"
          >
            <Zap size={12} className="text-amber-400" />
            <span className="text-slate-300">{executionTime}ms</span>
          </motion.div>
        )}
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-2">
        {isAuthenticated ? (
          <div className="flex items-center gap-2">
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/50 cursor-pointer"
            >
              {user?.avatar_url ? (
                <img src={user.avatar_url} className="w-6 h-6 rounded-full" alt="" />
              ) : (
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-[11px] font-bold text-white">
                  {(user?.username || user?.email || 'U')[0].toUpperCase()}
                </div>
              )}
              <span className="text-sm text-slate-300 hidden sm:block max-w-24 truncate">
                {user?.username || user?.email?.split('@')[0]}
              </span>
              <div className="hidden sm:flex items-center gap-1 px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-400 text-[10px] font-medium">
                <Zap size={10} />
                {user?.total_executions || 0}
              </div>
            </motion.div>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={logout}
              className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-red-400 transition-colors"
              title="Logout"
            >
              <LogOut size={16} />
            </motion.button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => openAuthModal('login')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-all shadow-lg shadow-indigo-500/25"
            >
              <LogIn size={14} />
              <span className="hidden sm:inline">Sign In</span>
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => openAuthModal('register')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-600 hover:border-indigo-500 text-slate-300 hover:text-white text-sm transition-all"
            >
              <UserPlus size={14} />
              <span className="hidden sm:inline">Sign Up</span>
            </motion.button>
          </div>
        )}
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={openSettingsModal}
          className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
        >
          <Settings size={16} />
        </motion.button>
      </div>
    </motion.nav>
  );
}

function NavButton({ icon: Icon, label, onClick, active }) {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-all ${
        active
          ? 'bg-indigo-500/20 text-indigo-400'
          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
      }`}
    >
      <Icon size={14} />
      {label}
    </motion.button>
  );
}
