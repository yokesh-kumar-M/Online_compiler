import { useEditorStore } from '../../store';
import { LANGUAGE_CONFIG } from '../../utils/constants';
import { Circle, Wifi, WifiOff } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function StatusBar() {
  const { language, code, executionTime } = useEditorStore();
  const [cursorPos, setCursorPos] = useState({ line: 1, col: 1 });
  const [online, setOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setOnline(true);
    const handleOffline = () => setOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Expose cursor position setter for Monaco
  useEffect(() => {
    window.__setCursorPos = setCursorPos;
  }, []);

  const langConfig = LANGUAGE_CONFIG[language];
  const charCount = code?.length || 0;
  const lineCount = code?.split('\n').length || 0;

  return (
    <div className="h-7 flex items-center justify-between px-4 bg-slate-900/95 border-t border-slate-700/50 text-[11px] text-slate-500 select-none">
      <div className="flex items-center gap-4">
        {/* Status */}
        <div className="flex items-center gap-1.5">
          <Circle
            size={8}
            className={`fill-current ${online ? 'text-emerald-400' : 'text-red-400'}`}
          />
          <span>{online ? 'Ready' : 'Offline'}</span>
        </div>

        {/* Execution time */}
        {executionTime !== null && (
          <span className="text-indigo-400">
            ⚡ {executionTime}ms
          </span>
        )}
      </div>

      <div className="flex items-center gap-4">
        {/* Cursor position */}
        <span>
          Ln {cursorPos.line}, Col {cursorPos.col}
        </span>

        {/* Character count */}
        <span>{charCount.toLocaleString()} chars</span>

        {/* Line count */}
        <span>{lineCount} lines</span>

        {/* Language */}
        <div className="flex items-center gap-1.5">
          <span>{langConfig?.icon}</span>
          <span className="text-slate-400">{langConfig?.name}</span>
        </div>

        {/* Encoding */}
        <span>UTF-8</span>
      </div>
    </div>
  );
}
