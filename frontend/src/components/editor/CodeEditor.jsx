import Editor from '@monaco-editor/react';
import { useEditorStore } from '../../store';
import { LANGUAGE_CONFIG } from '../../utils/constants';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

export default function CodeEditor() {
  const { code, setCode, language } = useEditorStore();
  const langConfig = LANGUAGE_CONFIG[language];

  const handleMount = (editor, monaco) => {
    // Store editor reference for keyboard shortcuts
    window.__monacoEditor = editor;

    // Track cursor position
    editor.onDidChangeCursorPosition((e) => {
      if (window.__setCursorPos) {
        window.__setCursorPos({
          line: e.position.lineNumber,
          col: e.position.column,
        });
      }
    });

    // Focus the editor
    editor.focus();
  };

  return (
    <div className="flex-1 relative overflow-hidden">
      {/* Top gradient border */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent z-10" />

      <Editor
        height="100%"
        language={langConfig?.monaco || 'plaintext'}
        value={code}
        onChange={(value) => setCode(value || '')}
        onMount={handleMount}
        theme="vs-dark"
        loading={
          <div className="flex items-center justify-center h-full bg-slate-950">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
            >
              <Loader2 size={32} className="text-indigo-500" />
            </motion.div>
          </div>
        }
        options={{
          fontSize: 14,
          fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace",
          fontLigatures: true,
          lineNumbers: 'on',
          wordWrap: 'on',
          minimap: { enabled: true, maxColumn: 80, renderCharacters: false },
          scrollBeyondLastLine: false,
          renderLineHighlight: 'all',
          cursorBlinking: 'smooth',
          cursorSmoothCaretAnimation: 'on',
          smoothScrolling: true,
          folding: true,
          matchBrackets: 'always',
          autoIndent: 'advanced',
          formatOnPaste: true,
          tabSize: 4,
          bracketPairColorization: { enabled: true },
          guides: { bracketPairs: true, indentation: true },
          padding: { top: 16, bottom: 16 },
          renderWhitespace: 'selection',
          suggest: { showMethods: true, showFunctions: true },
          quickSuggestions: true,
          parameterHints: { enabled: true },
          autoClosingBrackets: 'always',
          autoClosingQuotes: 'always',
          links: true,
          colorDecorators: true,
          contextmenu: true,
          scrollbar: {
            verticalScrollbarSize: 8,
            horizontalScrollbarSize: 8,
          },
        }}
      />
    </div>
  );
}
