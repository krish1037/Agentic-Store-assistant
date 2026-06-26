import React, { useState, useEffect } from 'react';
import { Sparkles, RefreshCw, AlertTriangle } from 'lucide-react';
import { ConversationHistory } from '../components/ConversationHistory';
import { ChatWindow } from '../components/ChatWindow';
import { ChatInput } from '../components/ChatInput';
import type { ChatMessage } from '../types/chat';
import { sendMessage, getHistory } from '../services/api';

export const Home: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState('');
  const [backendHealth, setBackendHealth] = useState<'checking' | 'healthy' | 'unhealthy'>('checking');

  // Initialize unique session ID once per browser session
  useEffect(() => {
    let storedSessionId = sessionStorage.getItem('agentic_store_session_id');
    if (!storedSessionId) {
      storedSessionId = crypto.randomUUID();
      sessionStorage.setItem('agentic_store_session_id', storedSessionId);
    }
    setSessionId(storedSessionId);
    checkHealth();
  }, []);

  // Fetch history when sessionId is determined
  useEffect(() => {
    if (!sessionId) return;

    const fetchSessionHistory = async () => {
      try {
        const historyData = await getHistory(sessionId);
        if (historyData && historyData.messages) {
          setMessages(historyData.messages);
        }
      } catch (err) {
        console.error("Failed to load conversation history:", err);
      }
    };

    fetchSessionHistory();
  }, [sessionId]);

  const checkHealth = async () => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
    try {
      const res = await fetch(`${baseUrl}/health`);
      if (res.ok) {
        setBackendHealth('healthy');
      } else {
        setBackendHealth('unhealthy');
      }
    } catch {
      setBackendHealth('unhealthy');
    }
  };

  const handleSendMessage = async (userMessage: string) => {
    setError(null);
    setIsLoading(true);

    // Create user message object
    const newMsg: ChatMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };

    // Optimistically update local message list
    setMessages((prev) => [...prev, newMsg]);

    try {
      const result = await sendMessage(userMessage, sessionId);
      
      // Create assistant message object containing intermediate steps
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: result.response,
        timestamp: new Date().toISOString(),
        reasoning_steps: result.reasoning_steps,
        tool_calls: result.tool_calls,
        used_rag: result.used_rag
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err.message || "An error occurred while contacting the support assistant.");
    } finally {
      setIsLoading(false);
    }
  };

  const resetSession = () => {
    const newSessionId = crypto.randomUUID();
    sessionStorage.setItem('agentic_store_session_id', newSessionId);
    setSessionId(newSessionId);
    setMessages([]);
    setError(null);
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      
      {/* SIDEBAR: CONVERSATIONAL MEMORY */}
      <ConversationHistory messages={messages} currentSessionId={sessionId} />

      {/* MAIN CONTAINER */}
      <div className="flex-1 flex flex-col h-full bg-slate-900/10">
        
        {/* Top Navbar */}
        <header className="px-6 py-4 border-b border-slate-900 bg-slate-950 flex items-center justify-between shadow-sm shrink-0">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-brand-400" />
            <div>
              <h2 className="text-sm font-bold text-slate-100 m-0">Store Assistant Agent</h2>
              <p className="text-[10px] text-slate-500 m-0">Gemini 2.5 Flash orchestrating retail tools</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            
            {/* Status indicators */}
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-400 font-medium">Backend:</span>
              <div className="flex items-center gap-1.5">
                <span className={`w-2 h-2 rounded-full ${
                  backendHealth === 'healthy' ? 'bg-emerald-500 animate-pulse' : backendHealth === 'checking' ? 'bg-amber-500' : 'bg-rose-500'
                }`}></span>
                <span className="text-[10px] text-slate-350 capitalize font-medium">{backendHealth}</span>
              </div>
            </div>

            <button
              onClick={resetSession}
              className="flex items-center gap-1 text-[11px] bg-slate-900 border border-slate-800 text-slate-300 hover:text-white px-2.5 py-1.5 rounded-lg transition-colors active:scale-[0.98]"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reset Session</span>
            </button>
          </div>
        </header>

        {/* ERROR NOTIFIER */}
        {error && (
          <div className="mx-6 mt-4 p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <div className="flex-1 font-medium">{error}</div>
            <button 
              onClick={() => checkHealth()} 
              className="text-[10px] bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded uppercase hover:bg-rose-500/30 transition-colors"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* CHAT DISPLAY */}
        <ChatWindow 
          messages={messages} 
          isLoading={isLoading} 
          onSelectSuggestedQuery={handleSendMessage} 
        />

        {/* MESSAGE CONTROL INPUT */}
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />

      </div>
    </div>
  );
};
