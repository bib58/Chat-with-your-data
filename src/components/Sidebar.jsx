import { useState, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, FileSpreadsheet, CheckCircle2, Loader2, Database } from 'lucide-react';

export default function Sidebar({ dataset, setDataset }) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
      setError('Please upload a CSV or Excel file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setDataset(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Upload failed. Is backend running?');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-72 bg-slate-900 border-r border-slate-800 flex flex-col shadow-2xl z-20 relative">
      <div className="p-6 border-b border-slate-800">
        <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400 flex items-center gap-2">
          <Database className="w-6 h-6 text-indigo-400" />
          Data Hub
        </h2>
      </div>

      <div className="p-6 flex-1 overflow-y-auto space-y-6">
        <div>
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
            Data Source
          </h3>
          
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="group relative overflow-hidden rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 hover:border-indigo-500/50 transition-all cursor-pointer p-6 flex flex-col items-center justify-center gap-3 text-center"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
            
            {isUploading ? (
              <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            ) : dataset ? (
              <CheckCircle2 className="w-8 h-8 text-emerald-400" />
            ) : (
              <UploadCloud className="w-8 h-8 text-indigo-400 group-hover:-translate-y-1 transition-transform" />
            )}
            
            <div>
              <p className="font-medium text-slate-200">
                {dataset ? 'Dataset Ready' : 'Upload Data'}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                {dataset ? dataset.filename : 'CSV or Excel formats'}
              </p>
            </div>
            
            <input 
              type="file" 
              className="hidden" 
              ref={fileInputRef} 
              accept=".csv,.xlsx" 
              onChange={handleFileUpload}
            />
          </div>
          
          {error && (
            <p className="text-red-400 text-xs mt-3 text-center">{error}</p>
          )}
        </div>
      </div>
      
      <div className="p-4 border-t border-slate-800 bg-slate-900/50 text-xs text-slate-500 text-center">
        Powered by LangGraph & Gemini
      </div>
    </div>
  );
}
