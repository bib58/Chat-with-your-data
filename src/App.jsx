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
    <div className="flex h-screen w-screen overflow-hidden bg-slate-900 text-slate-100 font-sans selection:bg-indigo-500/30 print:h-auto print:overflow-visible print:block">
      <Sidebar dataset={dataset} setDataset={setDataset} />
      <div className="flex-1 flex flex-col relative h-full print:h-auto print:overflow-visible print:block">
        {dataset ? (
          <ChatInterface dataset={dataset} />
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
            <div className="w-24 h-24 mb-6 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center opacity-80 blur-xl animate-pulse absolute z-0" />
            <div className="w-20 h-20 mb-6 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-2xl shadow-indigo-500/20 z-10">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400 mb-4 z-10">
              Conversational Analytics
            </h1>
            <p className="text-slate-400 max-w-md z-10 text-lg">
              Upload a dataset from the sidebar to start asking questions in natural language.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
