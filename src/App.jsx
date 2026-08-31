import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';

function App() {
  const [dataset, setDataset] = useState(null);
  
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (dataset && dataset.dataset_path) {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        fetch(`${API_URL}/cleanup`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ dataset_path: dataset.dataset_path }),
          keepalive: true
        }).catch(err => console.error("Cleanup failed:", err));
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [dataset]);
  
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30 print:h-auto print:overflow-visible print:block relative">
      {/* Global Background Glow */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none mix-blend-screen" />
      <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen" />
      
      <Sidebar dataset={dataset} setDataset={setDataset} />
      <div className="flex-1 flex flex-col relative h-full print:h-auto print:overflow-visible print:block z-10 bg-slate-950/50">
        {dataset ? (
          <ChatInterface dataset={dataset} />
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center relative">
            <div className="w-32 h-32 mb-8 rounded-full bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center opacity-60 blur-2xl animate-pulse-slow absolute z-0" />
            <div className="w-24 h-24 mb-8 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 flex items-center justify-center shadow-[0_0_40px_-10px_rgba(99,102,241,0.5)] z-10 rotate-3 hover:rotate-0 transition-transform duration-500">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-transparent bg-clip-text bg-gradient-to-br from-indigo-400 to-purple-400" fill="currentColor" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h1 className="text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-indigo-200 to-purple-300 mb-6 z-10 drop-shadow-sm">
              Conversational Analytics
            </h1>
            <p className="text-slate-400 max-w-lg z-10 text-lg leading-relaxed font-light">
              Connect your database or upload a dataset to explore your data using natural language.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
