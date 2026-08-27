import { Bot, User, Code, FileText, BarChart3, Table as TableIcon } from 'lucide-react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, ScatterChart, Scatter, 
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';

const COLORS = ['#6366f1', '#a855f7', '#ec4899', '#14b8a6', '#f59e0b', '#3b82f6'];

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex gap-4 max-w-[85%] ${isUser ? 'ml-auto flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 shadow-lg ${
        isUser 
          ? 'bg-slate-700 text-slate-300 border border-slate-600' 
          : 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
      }`}>
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>
      
      <div className={`flex flex-col gap-2 ${isUser ? 'items-end' : 'items-start'}`}>
        
        {message.type === 'text' && (
          <div className={`px-5 py-4 rounded-2xl shadow-sm text-[15px] leading-relaxed ${
            isUser 
              ? 'bg-indigo-600 text-white rounded-tr-sm shadow-indigo-900/20' 
              : 'bg-slate-800 text-slate-200 border border-slate-700/50 rounded-tl-sm'
          }`}>
            <div className="whitespace-pre-wrap">{message.content}</div>
          </div>
        )}
        
        {message.query && !isUser && (
          <div className="mt-1 bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-inner max-w-full overflow-x-auto w-full">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-500 mb-2 uppercase tracking-wider">
              <Code className="w-3.5 h-3.5" /> Generated Pandas Code
            </div>
            <pre className="text-sm font-mono text-emerald-400/90 whitespace-pre-wrap">
              {message.query}
            </pre>
          </div>
        )}

        {message.type === 'table' && message.data && message.data.length > 0 && (
          <div className="mt-2 bg-slate-800 border border-slate-700/50 rounded-xl overflow-hidden shadow-lg w-full max-w-full overflow-x-auto">
             <div className="bg-slate-900/50 px-4 py-2 border-b border-slate-700/50 flex items-center gap-2 text-sm text-slate-300 font-medium">
               <TableIcon className="w-4 h-4 text-indigo-400" /> Data View
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
          <div className="mt-2 bg-slate-800 border border-slate-700/50 rounded-xl p-4 shadow-lg w-full min-w-[500px]">
            <div className="flex items-center gap-2 text-sm text-slate-300 font-medium mb-4">
               <BarChart3 className="w-4 h-4 text-purple-400" /> {message.config.title}
            </div>
            <div className="h-[300px] w-full">
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
