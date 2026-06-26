import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [text, setText] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || isLoading) return;
    onSendMessage(text);
    setText('');
  };

  // Focus input field on load or when loading completes
  useEffect(() => {
    if (!isLoading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading]);

  return (
    <form onSubmit={handleSubmit} className="border-t border-slate-900 bg-slate-950 p-4">
      <div className="relative flex items-center max-w-4xl mx-auto">
        <input
          ref={inputRef}
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={isLoading}
          placeholder={isLoading ? 'Agent is thinking/calling tools...' : 'Ask about orders (ORD-1002), products (P101), alternatives, or policies...'}
          className="w-full pl-4 pr-12 py-3 bg-slate-900 border border-slate-800 rounded-xl text-slate-100 text-sm placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500/20 disabled:opacity-50 transition-all font-sans"
          id="chat-message-input"
        />
        <button
          type="submit"
          disabled={!text.trim() || isLoading}
          className="absolute right-2 p-2 rounded-lg bg-brand-500 text-white hover:bg-brand-600 disabled:opacity-30 disabled:hover:bg-brand-500 transition-colors shrink-0"
          aria-label="Send Message"
          id="chat-send-button"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </div>
    </form>
  );
};
