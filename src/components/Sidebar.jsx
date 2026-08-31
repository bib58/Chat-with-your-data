import { useState, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, FileSpreadsheet, CheckCircle2, Loader2, Database, Link, AlertCircle } from 'lucide-react';

export default function Sidebar({ dataset, setDataset }) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [connectionString, setConnectionString] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx') && !file.name.endsWith('.json')) {
      setError('Please upload a CSV, Excel, or JSON file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    setError('');

    try {
      const API_URL = import.meta.env.VITE_API_URL;
      const response = await axios.post(`${API_URL}/upload`, formData, {
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

  const handleConnect = async () => {
    if (!connectionString.trim()) {
      setError('Please enter a connection string.');
      return;
    }

    setIsConnecting(true);
    setError('');

    try {
      const API_URL = import.meta.env.VITE_API_URL;
      const response = await axios.post(`${API_URL}/connect`, {
        connection_string: connectionString.trim()
      });
      setDataset(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Connection failed. Check your link.');
    } finally {
      setIsConnecting(false);
    }
  };

  return (
    <div className="w-72 bg-slate-900/60 backdrop-blur-2xl border-r border-slate-800/50 flex flex-col shadow-2xl z-20 relative print:hidden transition-all duration-300">
      <div className="p-6 border-b border-slate-800">
        <h2 className="text-xl font-bold bg-clip-text text-transparent bg-linear-to-r from-indigo-400 to-purple-400 flex items-center gap-2">
          <Database className="w-6 h-6 text-indigo-400" />
          Data Hub
        </h2>
      </div>

      <div className="p-6 flex-1 overflow-y-auto space-y-6">
        <div>
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
            Upload File
          </h3>

          <div
            onClick={() => fileInputRef.current?.click()}
            className="group relative overflow-hidden rounded-xl bg-slate-800/40 hover:bg-slate-800/80 border border-slate-700/50 hover:border-indigo-400 hover:shadow-[0_0_20px_-5px_rgba(99,102,241,0.3)] transition-all duration-300 cursor-pointer p-8 flex flex-col items-center justify-center gap-3 text-center"
          >
            <div className="absolute inset-0 bg-linear-to-br from-indigo-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            {isUploading ? (
              <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            ) : dataset && dataset.dataset_path ? (
              <CheckCircle2 className="w-8 h-8 text-emerald-400" />
            ) : (
              <UploadCloud className="w-8 h-8 text-indigo-400 transition-transform" />
            )}

            <div>
              <p className="font-medium text-slate-200">
                {dataset && dataset.dataset_path ? 'Dataset Ready' : 'Upload Data'}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                {dataset && dataset.dataset_path ? dataset.filename : 'CSV, Excel, or JSON formats'}
              </p>
            </div>

            <input type="file" className="hidden" ref={fileInputRef} accept=".csv,.xlsx" onChange={handleFileUpload} />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-slate-700/60"></div>
          <span className="text-xs text-slate-500 font-medium">OR</span>
          <div className="flex-1 h-px bg-slate-700/60"></div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Link className="w-3.5 h-3.5" />
            SQL Server Link
          </h3>

          {dataset && dataset.db_uri ? (
            <div className="rounded-xl bg-emerald-500/10 border border-emerald-500/30 p-4 flex flex-col items-center gap-2 text-center">
              <CheckCircle2 className="w-8 h-8 text-emerald-400" />
              <p className="font-medium text-emerald-300 text-sm">Connected</p>
              <p className="text-xs text-slate-400 break-all">{dataset.filename}</p>
              <button
                onClick={() => { setDataset(null); setConnectionString(''); }}
                className="mt-2 text-xs text-slate-500 hover:text-red-400 transition-colors"
              >
                Disconnect
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <textarea
                value={connectionString}
                onChange={(e) => setConnectionString(e.target.value)}
                placeholder={"mssql+pymssql://user:pass@server:1433/dbname"}
                className="w-full bg-slate-950/50 border border-slate-700/60 focus:border-indigo-400 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-4 focus:ring-indigo-500/10 resize-none transition-all duration-300 shadow-inner"
                rows={3}
              />
              <button
                onClick={handleConnect}
                disabled={isConnecting || !connectionString.trim()}
                className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 text-white text-sm font-medium py-2.5 px-4 rounded-lg transition-colors shadow-lg shadow-indigo-500/20"
              >
                {isConnecting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Database className="w-4 h-4" />
                    Connect
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {error && (
          <div className="flex items-start gap-2 text-red-400 text-xs bg-red-500/10 border border-red-500/20 rounded-lg p-3">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <p>{error}</p>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-slate-800 bg-slate-900/50 text-xs text-slate-500 text-center">
        Powered by LangGraph & Gemini
      </div>
    </div>
  );
}
