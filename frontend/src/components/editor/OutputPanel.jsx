import { motion, AnimatePresence } from 'framer-motion';
import { useEditorStore } from '../../store';
import {
  Terminal, Type, Trash2, Copy, CheckCircle2, XCircle,
  Clock, Maximize2, Minimize2, ChevronRight
} from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import toast from 'react-hot-toast';

export default function OutputPanel() {
  const { output, stdin, setStdin, activeOutputTab, setActiveOutputTab, clearOutput, isRunning, executionTime } = useEditorStore();
  const [isMaximized, setIsMaximized] = useState(false);
  const outputRef = useRef(null);

  // Auto scroll to bottom on new output
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  const copyOutput = () => {
    if (output?.content) {
      navigator.clipboard.writeText(output.content);
      toast.success('Output copied!');
    }
  };

  const tabs = [
    { id: 'output', label: 'Output', icon: Terminal },
    { id: 'stdin', label: 'Input', icon: Type },
  ];

  return (
    <motion.div
      layout
      className={`flex flex-col border-l border-slate-700/50 bg-slate-950/80 ${
        isMaximized ? 'fixed inset-0 z-50' : ''
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-slate-700/50 bg-slate-900/80">
        <div className="flex items-center gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveOutputTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  activeOutputTab === tab.id
                    ? 'bg-indigo-500/20 text-indigo-400 shadow-sm'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800'
                }`}
              >
                <Icon size={12} />
                {tab.label}
                {tab.id === 'output' && output && (
                  <span className={`w-1.5 h-1.5 rounded-full ${output.success ? 'bg-emerald-400' : 'bg-red-400'}`} />
                )}
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-1">
          {executionTime !== null && activeOutputTab === 'output' && (
            <div className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-800 text-[10px] text-slate-400 mr-1">
              <Clock size={10} />
              {executionTime}ms
            </div>
          )}
          <button
            onClick={copyOutput}
            className="p-1 rounded hover:bg-slate-800 text-slate-500 hover:text-slate-300 transition-colors"
            title="Copy output"
          >
            <Copy size={13} />
          </button>
          <button
            onClick={clearOutput}
            className="p-1 rounded hover:bg-slate-800 text-slate-500 hover:text-slate-300 transition-colors"
            title="Clear output"
          >
            <Trash2 size={13} />
          </button>
          <button
            onClick={() => setIsMaximized(!isMaximized)}
            className="p-1 rounded hover:bg-slate-800 text-slate-500 hover:text-slate-300 transition-colors"
          >
            {isMaximized ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        <AnimatePresence mode="wait">
          {activeOutputTab === 'output' ? (
            <motion.div
              key="output"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              ref={outputRef}
              className="h-full overflow-y-auto p-4 font-mono text-sm leading-relaxed"
            >
              {isRunning ? (
                <div className="flex flex-col items-center justify-center h-full gap-3">
                  <div className="relative">
                    <div className="w-12 h-12 rounded-full border-2 border-slate-700 border-t-indigo-500 animate-spin" />
                    <div className="absolute inset-0 w-12 h-12 rounded-full border-2 border-transparent border-b-purple-500 animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }} />
                  </div>
                  <p className="text-slate-400 text-sm animate-pulse">Executing code...</p>
                </div>
              ) : output ? (
                <motion.div initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
                  {/* Status badge */}
                  <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium mb-3 ${
                    output.success
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-red-500/10 text-red-400 border border-red-500/20'
                  }`}>
                    {output.success ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                    {output.success ? 'Success' : 'Error'}
                    {executionTime !== null && (
                      <span className="text-slate-500 ml-1">• {executionTime}ms</span>
                    )}
                  </div>

                  {/* Output content */}
                  <pre className={`whitespace-pre-wrap break-all ${
                    output.success ? 'text-slate-200' : 'text-red-300'
                  }`}>
                    {output.content}
                  </pre>
                </motion.div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 flex items-center justify-center mb-4 border border-indigo-500/20">
                    <Terminal size={28} className="text-indigo-400/60" />
                  </div>
                  <h3 className="text-slate-400 font-medium mb-1">No Output Yet</h3>
                  <p className="text-slate-600 text-xs max-w-xs">
                    Click <span className="text-emerald-400 font-semibold">Run</span> or press{' '}
                    <kbd className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px] font-mono border border-slate-700">
                      Ctrl+Enter
                    </kbd>{' '}
                    to execute your code
                  </p>
                  <div className="mt-4 flex items-center gap-2 text-[10px] text-slate-600">
                    <ChevronRight size={10} />
                    <span>Supports Python, JavaScript, C, C++, Java, Go</span>
                  </div>
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="stdin"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full p-4"
            >
              <div className="mb-2 flex items-center gap-2">
                <Type size={14} className="text-slate-500" />
                <span className="text-xs text-slate-500">Standard Input (stdin)</span>
              </div>
              <textarea
                value={stdin}
                onChange={(e) => setStdin(e.target.value)}
                placeholder="Enter input for your program here...&#10;Each line will be read as input."
                className="w-full h-[calc(100%-2rem)] bg-slate-900/50 border border-slate-700/50 rounded-xl p-3 text-sm text-slate-200 font-mono resize-none outline-none focus:border-indigo-500/50 placeholder-slate-600 transition-colors"
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
