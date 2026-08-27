import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Loader2, Bot, User, Code, FileDown } from 'lucide-react';
import MessageBubble from './MessageBubble';

export default function ChatInterface({ dataset }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Dataset **${dataset.filename}** loaded successfully! What would you like to know?`,
      type: 'text'
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage, type: 'text' }]);
    setIsTyping(true);

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        message: userMessage,
        session_id: 'default',
        dataset_path: dataset.dataset_path
      });

      const data = response.data;
      
      const newMessages = [];
      
      if (data.answer) {
        newMessages.push({
          role: 'assistant',
          content: data.answer,
          type: 'text',
          query: data.query_executed
        });
      }

      if (data.table_data) {
        newMessages.push({
          role: 'assistant',
          content: '',
          type: 'table',
          data: data.table_data
        });
      }

      if (data.chart_config && data.table_data) {
        newMessages.push({
          role: 'assistant',
          content: '',
          type: 'chart',
          data: data.table_data,
          config: data.chart_config
        });
      }

      setMessages(prev => [...prev, ...newMessages]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: error.response?.data?.detail || 'An error occurred while processing your request.', 
        type: 'text' 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-0 h-full bg-slate-950 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 to-slate-950">
      
      <header className="h-16 shrink-0 border-b border-slate-800/60 bg-slate-900/50 backdrop-blur-md flex items-center px-6 sticky top-0 z-10 justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center">
            <Bot className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h2 className="font-semibold text-slate-200">Analytics Agent</h2>
            <p className="text-xs text-emerald-400 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Online
            </p>
          </div>
        </div>
        <button onClick={() => window.print()} className="flex items-center gap-2 text-slate-400 hover:text-indigo-400 transition-colors text-sm px-3 py-1.5 rounded-md hover:bg-slate-800">
          <FileDown className="w-4 h-4" />
          Export PDF
        </button>
      </header>

      <div className="flex-1 min-h-0 overflow-y-auto p-6 space-y-6 custom-scrollbar">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}
        
        {isTyping && (
          <div className="flex gap-4 max-w-3xl">
            <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center shrink-0 mt-1">
              <Bot className="w-5 h-5 text-indigo-400" />
            </div>
            <div className="bg-slate-800 border border-slate-700/50 rounded-2xl rounded-tl-sm px-5 py-4 text-slate-200 flex items-center gap-2 shadow-lg">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce"></span>
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '0.4s' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-slate-900/80 backdrop-blur-xl border-t border-slate-800/60">
        <div className="max-w-4xl mx-auto relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
          <div className="relative flex items-end gap-2 bg-slate-900 border border-slate-700 focus-within:border-indigo-500 rounded-2xl p-2 shadow-2xl transition-colors">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your data... (e.g. 'Show me sales by region')"
              className="w-full max-h-32 min-h-[44px] bg-transparent resize-none text-slate-200 placeholder:text-slate-500 focus:outline-none py-3 px-4"
              rows={1}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isTyping}
              className="w-11 h-11 rounded-xl bg-indigo-500 hover:bg-indigo-600 disabled:opacity-50 disabled:hover:bg-indigo-500 text-white flex items-center justify-center shrink-0 transition-colors shadow-lg shadow-indigo-500/25"
            >
              {isTyping ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5 ml-1" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
