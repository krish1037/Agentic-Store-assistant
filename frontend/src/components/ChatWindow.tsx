import React, { useEffect, useRef } from 'react';
import { Sparkles, HelpCircle } from 'lucide-react';
import type { ChatMessage } from '../types/chat';
import { MessageBubble } from './MessageBubble';

interface ChatWindowProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSelectSuggestedQuery: (query: string) => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  onSelectSuggestedQuery
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  const suggestedQueries = [
    {
      label: "Order Status Check",
      desc: "Where is order ORD-1002?",
      query: "Where is order ORD-1002?"
    },
    {
      label: "Product Lookup",
      desc: "Tell me about product P101",
      query: "Tell me about product P101"
    },
    {
      label: "Find Cheaper Alternative",
      desc: "Is there a cheaper alternative to the shoes I ordered?",
      query: "Is there a cheaper alternative to the shoes I ordered?"
    },
    {
      label: "Store Return Policy",
      desc: "Can I return my shoes after 15 days?",
      query: "Can I return my shoes after 15 days?"
    }
  ];

  // Auto scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto bg-slate-900/20 p-6 space-y-6 flex flex-col">
      {messages.length === 0 ? (
        
        // Welcome Empty State
        <div className="my-auto max-w-2xl mx-auto text-center space-y-8 p-4">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-brand-500/10 border border-brand-500/20 text-brand-400 flex items-center justify-center mx-auto shadow-md">
              <Sparkles className="w-6 h-6 animate-pulse" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-100 font-sans">
              Agentic Store Assistant
            </h1>
            <p className="text-sm text-slate-400 max-w-md mx-auto leading-normal">
              An intelligent, tool-calling customer support dashboard. Select an assignment scenario below or ask your own question to test.
            </p>
          </div>

          {/* Scenarios Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {suggestedQueries.map((item, idx) => (
              <button
                key={idx}
                onClick={() => onSelectSuggestedQuery(item.query)}
                className="p-4 rounded-xl border border-slate-850 bg-slate-900/40 hover:bg-slate-850/50 hover:border-slate-700 text-left transition-all hover:scale-[1.01] active:scale-[0.99] flex gap-3 group shadow-sm"
              >
                <HelpCircle className="w-5 h-5 text-brand-400 shrink-0 mt-0.5 group-hover:rotate-12 transition-transform" />
                <div className="space-y-1">
                  <div className="text-xs font-semibold text-slate-200">{item.label}</div>
                  <div className="text-xs text-slate-400 font-medium">"{item.desc}"</div>
                </div>
              </button>
            ))}
          </div>
        </div>

      ) : (
        
        // Chat Thread
        <div className="space-y-6 max-w-4xl w-full mx-auto flex-1">
          {messages.map((msg, idx) => (
            <MessageBubble key={idx} message={msg} />
          ))}

          {/* Typing Indicator */}
          {isLoading && (
            <div className="flex gap-3 max-w-[85%] mr-auto items-end">
              <div className="w-8 h-8 rounded-full bg-slate-900 border border-slate-800 text-slate-400 flex items-center justify-center shrink-0">
                <Sparkles className="w-4 h-4 animate-spin" />
              </div>
              <div className="bg-slate-900/30 border border-slate-800 rounded-2xl rounded-tl-none p-3.5 flex items-center gap-1.5 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-slate-450 dot-pulse-delay-1"></span>
                <span className="w-1.5 h-1.5 rounded-full bg-slate-450 dot-pulse-delay-2"></span>
                <span className="w-1.5 h-1.5 rounded-full bg-slate-450 dot-pulse-delay-3"></span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
};
