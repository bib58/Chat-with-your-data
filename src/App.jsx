import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';

function App() {
  const [dataset, setDataset] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (dataset && dataset.dataset_path) {
        const API_URL = import.meta.env.VITE_API_URL;
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
      <div className="absolute top-0 left-1/4 w-125 h-125 bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none mix-blend-screen" />
      <div className="absolute bottom-0 right-1/4 w-150 h-150 bg-purple-600/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen" />
      
      <Sidebar dataset={dataset} setDataset={setDataset} isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />
      
      {/* Mobile overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-20 md:hidden transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      <div className="flex-1 flex flex-col relative h-full print:h-auto print:overflow-visible print:block z-10 bg-slate-950/50 w-full min-w-0">
        {dataset ? (
          <ChatInterface dataset={dataset} onOpenSidebar={() => setIsSidebarOpen(true)} />
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center relative w-full h-full">
            <div className="absolute top-6 left-6 md:hidden">
              <button 
                onClick={() => setIsSidebarOpen(true)}
                className="p-2 -ml-2 rounded-lg text-slate-400 hover:text-indigo-400 hover:bg-slate-800/50 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
              </button>
            </div>
            
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-linear-to-r from-white via-indigo-200 to-purple-300 mb-6 z-10 drop-shadow-sm px-4">
              Conversational Analytics
            </h1>
            <p className="text-slate-400 max-w-lg z-10 text-base md:text-lg leading-relaxed font-light px-4">
              Connect your database or upload a dataset to explore your data using natural language.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
