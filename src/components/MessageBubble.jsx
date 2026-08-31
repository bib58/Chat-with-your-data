import { useState } from 'react';
import { User, Code, BarChart3, Table as TableIcon, Copy, Check } from 'lucide-react';
import botImg from '../assets/bot.png';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#6366f1', '#a855f7', '#ec4899', '#14b8a6', '#f59e0b', '#3b82f6'];

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const [codeCopied, setCodeCopied] = useState(false);

  const handleCopy = async () => {
    let textToCopy = message.content || '';
    if (!textToCopy && message.query) {
      textToCopy = message.query;
    } else if (!textToCopy && message.data) {
      textToCopy = JSON.stringify(message.data, null, 2);
    }

    if (!textToCopy) return;

    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(textToCopy);
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = textToCopy;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  const handleCopyCode = async () => {
    if (!message.query) return;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(message.query);
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = message.query;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }
      setCodeCopied(true);
      setTimeout(() => setCodeCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code: ', err);
    }
  };

  return (
    <div className={`flex gap-3.5 max-w-[88%] animate-message-enter ${isUser ? 'ml-auto flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 shadow-lg overflow-hidden ${isUser
          ? 'bg-slate-700 text-slate-300 border border-slate-600'
          : 'bg-indigo-500/20 border border-indigo-500/30'
        }`}>
        {isUser ? <User className="w-4 h-4" /> : <img src={botImg} alt="Bot" className="w-full h-full object-cover" />}
      </div>

      <div className={`flex flex-col gap-2.5 min-w-0 max-w-full ${isUser ? 'items-end' : 'items-start'}`}>

        {message.type === 'text' && message.content && (
          <div className={`group relative px-5 py-4 rounded-2xl shadow-sm text-[14.5px] leading-relaxed transition-all ${isUser
              ? 'bg-linear-to-br from-indigo-500 to-purple-600 text-white rounded-tr-sm shadow-lg shadow-indigo-500/20 pr-11'
              : 'bg-slate-800/80 backdrop-blur-md text-slate-200 border border-slate-700/50 rounded-tl-sm pr-11 shadow-xl shadow-black/20'
            }`}>
            <button
              onClick={handleCopy}
              title={copied ? 'Copied!' : 'Copy message'}
              aria-label={copied ? 'Copied to clipboard' : 'Copy message to clipboard'}
              className={`absolute top-2.5 right-2.5 p-1.5 rounded-lg text-xs flex items-center gap-1 transition-all duration-200 cursor-pointer ${isUser
                  ? 'text-indigo-200 hover:text-white hover:bg-indigo-700/60 active:scale-95'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-700/70 active:scale-95'
                } ${copied ? 'opacity-100 text-emerald-400 hover:text-emerald-300' : 'opacity-70 group-hover:opacity-100'}`}
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-[11px] font-medium text-emerald-400 select-none">Copied</span>
                </>
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>

            <div className="markdown-content select-text overflow-hidden">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ node, ...props }) => (
                    <h1 className="text-xl font-bold text-white mt-3 mb-2 pb-1.5 border-b border-slate-700/60 first:mt-0" {...props} />
                  ),
                  h2: ({ node, ...props }) => (
                    <h2 className="text-lg font-bold text-slate-100 mt-3 mb-2 pb-1 border-b border-slate-700/40 first:mt-0" {...props} />
                  ),
                  h3: ({ node, ...props }) => (
                    <h3 className={`text-[15px] font-semibold mt-3 mb-1.5 first:mt-0 ${isUser ? 'text-white' : 'text-indigo-300'}`} {...props} />
                  ),
                  h4: ({ node, ...props }) => (
                    <h4 className="text-sm font-semibold text-slate-200 mt-2 mb-1 first:mt-0" {...props} />
                  ),
                  p: ({ node, ...props }) => (
                    <p className={`mb-2.5 last:mb-0 leading-relaxed ${isUser ? 'text-white' : 'text-slate-200'}`} {...props} />
                  ),
                  ul: ({ node, ...props }) => (
                    <ul className="list-disc list-outside pl-5 mb-3 space-y-1 text-slate-300 last:mb-0" {...props} />
                  ),
                  ol: ({ node, ...props }) => (
                    <ol className="list-decimal list-outside pl-5 mb-3 space-y-1 text-slate-300 last:mb-0" {...props} />
                  ),
                  li: ({ node, ...props }) => (
                    <li className="leading-relaxed pl-0.5" {...props} />
                  ),
                  strong: ({ node, ...props }) => (
                    <strong className="font-semibold text-white" {...props} />
                  ),
                  em: ({ node, ...props }) => (
                    <em className="italic text-slate-300" {...props} />
                  ),
                  hr: ({ node, ...props }) => (
                    <hr className="my-3.5 border-t border-slate-700/60" {...props} />
                  ),
                  blockquote: ({ node, ...props }) => (
                    <blockquote className="border-l-4 border-indigo-500/70 pl-3 py-1.5 my-2.5 text-slate-300 italic bg-slate-900/40 rounded-r-md" {...props} />
                  ),
                  code: ({ node, inline, className, children, ...props }) => {
                    const match = /language-(\w+)/.exec(className || '');
                    const isInlineCode = inline ?? (!match && !String(children).includes('\n'));
                    if (isInlineCode) {
                      return (
                        <code className={`px-1.5 py-0.5 mx-0.5 rounded font-mono text-[13px] ${isUser
                            ? 'bg-indigo-700/70 text-indigo-100 border border-indigo-500/40'
                            : 'bg-slate-900/90 text-indigo-300 border border-slate-700/60'
                          }`} {...props}>
                          {children}
                        </code>
                      );
                    }
                    return (
                      <code className={`block font-mono text-xs text-emerald-300 ${className || ''}`} {...props}>
                        {children}
                      </code>
                    );
                  },
                  pre: ({ node, ...props }) => (
                    <pre className="p-4 my-3 rounded-xl bg-slate-950/90 border border-slate-800/80 overflow-x-auto text-[13px] leading-relaxed font-mono custom-scrollbar shadow-inner" {...props} />
                  ),
                  table: ({ node, ...props }) => (
                    <div className="overflow-x-auto my-3 rounded-lg border border-slate-700/60">
                      <table className="min-w-full divide-y divide-slate-700 text-sm" {...props} />
                    </div>
                  ),
                  thead: ({ node, ...props }) => <thead className="bg-slate-900/80 text-slate-300 font-semibold" {...props} />,
                  tbody: ({ node, ...props }) => <tbody className="divide-y divide-slate-800/60 bg-slate-800/40" {...props} />,
                  tr: ({ node, ...props }) => <tr className="hover:bg-slate-700/30 transition-colors" {...props} />,
                  th: ({ node, ...props }) => <th className="px-3 py-2 text-left text-xs font-medium text-slate-300 uppercase tracking-wider" {...props} />,
                  td: ({ node, ...props }) => <td className="px-3 py-2 whitespace-nowrap text-xs text-slate-300" {...props} />
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {message.query && !isUser && (
          <div className="group relative mt-1 bg-slate-950/50 border border-slate-700/50 rounded-xl p-4 shadow-inner max-w-full overflow-x-auto w-full backdrop-blur-sm transition-all duration-300 hover:border-indigo-500/30 hover:shadow-indigo-500/5">
            <div className="flex items-center justify-between gap-2 text-xs font-mono text-slate-500 mb-2">
              <span className="flex items-center gap-1.5 uppercase tracking-wider text-slate-400">
                <Code className="w-3.5 h-3.5 text-indigo-400" /> Generated SQL Query
              </span>
              <button
                onClick={handleCopyCode}
                title={codeCopied ? 'Copied code!' : 'Copy code'}
                className="flex items-center gap-1 text-slate-400 hover:text-slate-200 px-2 py-1 rounded bg-slate-800/60 hover:bg-slate-800 border border-slate-700/40 transition-colors text-[11px]"
              >
                {codeCopied ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-400 font-medium">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
            <pre className="text-sm font-mono text-emerald-400/90 whitespace-pre-wrap">
              {message.query}
            </pre>
          </div>
        )}

        {message.type === 'table' && message.data && message.data.length > 0 && (
          <div className="group relative mt-2 bg-slate-800 border border-slate-700/50 rounded-xl overflow-hidden shadow-lg w-full max-w-full overflow-x-auto">
            <div className="bg-slate-900/70 px-4 py-2.5 border-b border-slate-700/50 flex items-center justify-between text-sm text-slate-300 font-medium">
              <div className="flex items-center gap-2">
                <TableIcon className="w-4 h-4 text-indigo-400" /> Data View
              </div>
              <button
                onClick={handleCopy}
                title={copied ? 'Copied!' : 'Copy table data as JSON'}
                className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 px-2 py-1 rounded bg-slate-800/80 hover:bg-slate-800 border border-slate-700/50 transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400 font-medium">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy JSON</span>
                  </>
                )}
              </button>
            </div>
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-slate-800/80 text-slate-400 border-b border-slate-700/50">
                <tr>
                  {Object.keys(message.data[0]).map(key => (
                    <th key={key} className="px-4 py-3">{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {message.data.slice(0, 10).map((row, i) => (
                  <tr key={i} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                    {Object.values(row).map((val, j) => (
                      <td key={j} className="px-4 py-2 whitespace-nowrap">{String(val)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {message.data.length > 10 && (
              <div className="px-4 py-2 text-xs text-center text-slate-500 bg-slate-800/30">
                Showing 10 of {message.data.length} rows
              </div>
            )}
          </div>
        )}

        {message.type === 'chart' && message.config && message.data && (
          <div className="mt-2 bg-slate-800 border border-slate-700/50 rounded-xl p-4 shadow-lg w-full md:min-w-125 overflow-x-auto">
            <div className="flex items-center gap-2 text-sm text-slate-300 font-medium mb-4">
              <BarChart3 className="w-4 h-4 text-purple-400" /> {message.config.title}
            </div>
            <div className="h-75 w-full min-w-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                {renderChart(message.config, message.data)}
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function renderChart(config, data) {
  const { type, xKey, yKey } = config;

  if (type === 'bar') {
    return (
      <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
        <XAxis dataKey={xKey} stroke="#94a3b8" fontSize={12} tickLine={false} />
        <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
        <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#f8fafc' }} />
        <Bar dataKey={yKey} fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={50} />
      </BarChart>
    );
  }

  if (type === 'line') {
    return (
      <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
        <XAxis dataKey={xKey} stroke="#94a3b8" fontSize={12} tickLine={false} />
        <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
        <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#f8fafc' }} />
        <Line type="monotone" dataKey={yKey} stroke="#a855f7" strokeWidth={3} dot={{ r: 4, fill: '#a855f7', strokeWidth: 0 }} activeDot={{ r: 6 }} />
      </LineChart>
    );
  }

  if (type === 'pie') {
    return (
      <PieChart>
        <Pie data={data} dataKey={yKey} nameKey={xKey} cx="50%" cy="50%" outerRadius={100} label>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#f8fafc' }} />
        <Legend />
      </PieChart>
    );
  }

  return (
    <ScatterChart margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
      <XAxis type="category" dataKey={xKey} name={xKey} stroke="#94a3b8" fontSize={12} />
      <YAxis type="number" dataKey={yKey} name={yKey} stroke="#94a3b8" fontSize={12} />
      <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
      <Scatter name={config.title} data={data} fill="#ec4899" />
    </ScatterChart>
  );
}
