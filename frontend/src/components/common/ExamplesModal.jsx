import { motion, AnimatePresence } from 'framer-motion';
import { useUIStore, useEditorStore } from '../../store';
import { X, Code2, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { compilerAPI } from '../../api/client';
import toast from 'react-hot-toast';

export default function ExamplesModal() {
  const { showExamplesModal, closeExamplesModal } = useUIStore();
  const { setCode, setLanguage } = useEditorStore();
  const [examples, setExamples] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (showExamplesModal && !examples) {
      fetchExamples();
    }
  }, [showExamplesModal]);

  const fetchExamples = async () => {
    setLoading(true);
    try {
      const { data } = await compilerAPI.examples();
      setExamples(data.examples);
    } catch {
      // Fallback examples
      setExamples({
        hello_world: {
          title: 'Hello World',
          language: 'python',
          code: '# Hello World\nprint("Hello, World!")\nprint("Welcome to CodeForge!")\n',
          description: 'A simple hello world program',
        },
        fibonacci: {
          title: 'Fibonacci Sequence',
          language: 'python',
          code: 'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nfor i in range(10):\n    print(f"F({i}) = {fibonacci(i)}")\n',
          description: 'Calculate Fibonacci numbers recursively',
        },
        data_structures: {
          title: 'Data Structures',
          language: 'python',
          code: '# Lists\nnumbers = [1, 2, 3, 4, 5]\nprint("List:", numbers)\nprint("Reversed:", numbers[::-1])\n\n# Dict\nperson = {"name": "Alice", "age": 30}\nprint("Person:", person)\n\n# Set\nunique = {1, 2, 3, 3, 4}\nprint("Set:", unique)\n',
          description: 'Common Python data structures',
        },
        sorting: {
          title: 'Sorting Algorithm',
          language: 'python',
          code: 'def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr\n\nnums = [64, 34, 25, 12, 22, 11, 90]\nprint("Original:", nums)\nprint("Sorted:", bubble_sort(nums.copy()))\n',
          description: 'Bubble sort implementation',
        },
      });
    } finally {
      setLoading(false);
    }
  };

  const loadExample = (example) => {
    setCode(example.code);
    if (example.language) setLanguage(example.language);
    closeExamplesModal();
    toast.success(`Loaded: ${example.title}`);
  };

  if (!showExamplesModal) return null;

  const iconColors = [
    'from-indigo-500 to-blue-600',
    'from-purple-500 to-pink-600',
    'from-emerald-500 to-teal-600',
    'from-amber-500 to-orange-600',
    'from-rose-500 to-red-600',
    'from-cyan-500 to-blue-600',
  ];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={(e) => e.target === e.currentTarget && closeExamplesModal()}
      >
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative w-full max-w-lg rounded-2xl glass border border-slate-600/30 shadow-2xl overflow-hidden"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 via-pink-500 to-amber-500" />

          <div className="p-6">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                  <Code2 size={20} className="text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Code Examples</h2>
                  <p className="text-xs text-slate-400">Choose a template to get started</p>
                </div>
              </div>
              <button
                onClick={closeExamplesModal}
                className="p-2 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 size={24} className="text-indigo-500 animate-spin" />
              </div>
            ) : (
              <div className="space-y-2 max-h-[50vh] overflow-y-auto pr-1">
                {examples && Object.entries(examples).map(([key, example], idx) => (
                  <motion.button
                    key={key}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    whileHover={{ scale: 1.01, x: 4 }}
                    onClick={() => loadExample(example)}
                    className="w-full flex items-center gap-3 p-3 rounded-xl bg-slate-800/40 border border-slate-700/30 hover:border-indigo-500/30 transition-all text-left group"
                  >
                    <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${iconColors[idx % iconColors.length]} flex items-center justify-center flex-shrink-0 group-hover:shadow-lg transition-shadow`}>
                      <Code2 size={18} className="text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">
                        {example.title}
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5 truncate">
                        {example.description || example.language || 'Python'}
                      </p>
                    </div>
                    <span className="text-xs text-slate-600 px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700/50">
                      {example.language || 'python'}
                    </span>
                  </motion.button>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
