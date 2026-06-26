import React from 'react';
import { User, Cpu } from 'lucide-react';
import type { ChatMessage } from '../types/chat';
import { ToolCallPanel } from './ToolCallPanel';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  // Format timestamps neatly
  const formatTime = (isoString: string): string => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <div className={`flex gap-3 max-w-[85%] ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}>
      
      {/* Icon Badge */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border ${
        isUser 
          ? 'bg-brand-500/10 border-brand-500/20 text-brand-400' 
          : 'bg-slate-900 border-slate-800 text-slate-300'
      }`}>
        {isUser ? <User className="w-4 h-4" /> : <Cpu className="w-4 h-4" />}
      </div>

      {/* Bubble Body */}
      <div className="flex flex-col space-y-1">
        
        {/* Name and time */}
        <div className={`flex items-center gap-2 text-[10px] text-slate-500 ${isUser ? 'justify-end' : ''}`}>
          <span className="font-semibold text-slate-400">{isUser ? 'You' : 'Store Assistant'}</span>
          <span>{formatTime(message.timestamp)}</span>
        </div>

        {/* Message Content */}
        {isUser ? (
          <div className="bg-brand-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-none text-sm font-sans shadow-md border border-brand-500/30">
            {message.content}
          </div>
        ) : (
          <div className="w-full">
            {/* If assistant response has reasoning/tools, embed in the transparent ToolCallPanel */}
            {message.reasoning_steps && message.tool_calls ? (
              <ToolCallPanel
                question={message.content}
                reasoningSteps={message.reasoning_steps || []}
                toolCalls={message.tool_calls || []}
                finalAnswer={message.content}
                usedRag={message.used_rag || false}
              />
            ) : (
              <div className="bg-slate-900/50 border border-slate-800 text-slate-200 px-4 py-2.5 rounded-2xl rounded-tl-none text-sm font-sans shadow-sm whitespace-pre-line">
                {message.content}
              </div>
            )}
          </div>
        )}
      </div>

    </div>
  );
};
