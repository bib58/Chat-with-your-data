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
