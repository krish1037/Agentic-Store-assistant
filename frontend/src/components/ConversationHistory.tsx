import React from 'react';
import { History, Brain, MessageSquare } from 'lucide-react';
import type { ChatMessage } from '../types/chat';

interface ConversationHistoryProps {
  messages: ChatMessage[];
  currentSessionId: string;
}

export const ConversationHistory: React.FC<ConversationHistoryProps> = ({
  messages,
  currentSessionId
}) => {
  // Check if a turn carries over context from memory (stretch goal)
  const carriesContext = (msg: ChatMessage, index: number): boolean => {
    if (msg.role !== 'assistant' || !msg.tool_calls || msg.tool_calls.length === 0) {
      return false;
    }

    // Find the corresponding user message (the prompt for this response)
    // In our list, user message is typically at index - 1
    const userMsg = messages[index - 1];
    if (!userMsg) return false;

    // Extract order or product IDs mentioned in tool calls of this turn
    const toolIDs: string[] = [];
    msg.tool_calls.forEach(tc => {
      const orderId = tc.tool_input.order_id;
      const productId = tc.tool_input.product_id;
      if (orderId) toolIDs.push(orderId.toUpperCase());
      if (productId) toolIDs.push(productId.toUpperCase());
    });

    if (toolIDs.length === 0) return false;

    // Check if any of these tool IDs were NOT mentioned in the user's prompt text
    const promptTextUpper = userMsg.content.toUpperCase();
    const hasUnmentionedId = toolIDs.some(id => !promptTextUpper.includes(id));

    // If it has an unmentioned ID that was used in a tool, it must have come from memory!
    return hasUnmentionedId;
  };

  return (
    <div className="w-80 border-r border-slate-900 bg-slate-950 flex flex-col h-full shrink-0">
      
      {/* Header */}
      <div className="p-4 border-b border-slate-900 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
          <History className="w-4 h-4 text-brand-400" />
          <span>Conversational Memory</span>
        </div>
        <span className="text-[10px] bg-slate-900 border border-slate-800 text-slate-400 px-1.5 py-0.5 rounded font-mono">
          {currentSessionId.slice(0, 8)}...
        </span>
      </div>

      {/* Memory Log List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-600 flex flex-col items-center gap-2">
            <MessageSquare className="w-8 h-8 text-slate-800" />
            <span>No conversation history yet. Start chatting to populate memory.</span>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            const contextRestored = carriesContext(msg, idx);

            return (
              <div 
                key={idx} 
                className={`p-3 rounded-lg border text-xs transition-all ${
                  isUser 
                    ? 'bg-slate-900/30 border-slate-850 text-slate-350' 
                    : 'bg-slate-900 border-slate-800 text-slate-200'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className={`text-[10px] font-bold uppercase tracking-wider ${
                    isUser ? 'text-slate-500' : 'text-brand-400'
                  }`}>
                    {isUser ? 'User Message' : 'Agent Response'}
                  </span>
                  
                  {/* Context Carried From Memory Badge */}
                  {!isUser && contextRestored && (
                    <span className="flex items-center gap-1 text-[9px] bg-brand-500/10 border border-brand-500/20 text-brand-400 px-1.5 py-0.5 rounded-full font-semibold animate-pulse">
                      <Brain className="w-2.5 h-2.5" />
                      <span>Memory Restored</span>
                    </span>
                  )}
                </div>

                <p className="line-clamp-3 leading-relaxed">
                  {msg.content}
                </p>
              </div>
            );
          })
        )}
      </div>

      {/* footer details */}
      <div className="p-3 border-t border-slate-900 bg-slate-900/10 text-[10px] text-slate-500 flex flex-col gap-1">
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-brand-500"></div>
          <span>In-memory Session Storage active</span>
        </div>
        <p className="text-[9px] leading-normal text-slate-600">
          This panel demonstrates the agent's context tracking. Pronoun queries like "Does it contain shoes?" resolve order details using session history.
        </p>
      </div>

    </div>
  );
};
