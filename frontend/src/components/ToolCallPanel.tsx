import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle2, Cpu, Wrench } from 'lucide-react';
import type { ToolCallRecord } from '../types/chat';

interface ToolCallPanelProps {
  question: string;
  reasoningSteps: string[];
  toolCalls: ToolCallRecord[];
  finalAnswer: string;
  usedRag: boolean;
}

export const ToolCallPanel: React.FC<ToolCallPanelProps> = ({
  question,
  reasoningSteps,
  toolCalls,
  finalAnswer,
  usedRag
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatToolOutput = (output: any): string => {
    if (!output) return 'No output';
    if (typeof output === 'string') return output;
    
    // Check order tool output
    if (output.found === true && output.order_id) {
      return `Order ${output.order_id} found (Customer: ${output.customer_name}, Status: ${output.status})`;
    }
    // Check product tool output
    if (output.found === true && output.product_id) {
      return `Product ${output.product_id} found (${output.name}, $${output.price})`;
    }
    // Check search tool output
    if (output.found === true && output.results) {
      return `Found ${output.results.length} products: ${output.results.map((p: any) => p.name).join(', ')}`;
    }
    // Check policy search output
    if (output.found === true && output.excerpts) {
      return `Policy matches in: ${output.sources.join(', ')}`;
    }
    // Fallback if not found or custom error
    if (output.found === false) {
      return `Not found: ${output.error || 'Item missing'}`;
    }
    
    return JSON.stringify(output);
  };

  return (
    <div className="mt-3 border border-slate-800 rounded-lg bg-slate-900/60 overflow-hidden shadow-md">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-slate-900 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-850/80 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-brand-400 animate-pulse" />
          <span>Agent Transparency Panel</span>
          {toolCalls.length > 0 && (
            <span className="bg-brand-500/10 text-brand-400 px-1.5 py-0.5 rounded text-[10px] border border-brand-500/20">
              {toolCalls.length} tool call{toolCalls.length > 1 ? 's' : ''}
            </span>
          )}
          {usedRag && (
            <span className="bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded text-[10px] border border-emerald-500/20">
              RAG Active
            </span>
          )}
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-slate-400">{isExpanded ? 'Hide Internals' : 'Inspect Internals'}</span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </button>

      {/* Dotted Flow Line Container */}
      {isExpanded && (
        <div className="p-4 border-t border-slate-850 bg-slate-950/40 text-xs space-y-4">
          
          {/* STEP 1: QUESTION */}
          <div className="relative pl-6 pb-2">
            <div className="absolute left-2 top-1 w-2 h-2 rounded-full bg-slate-700"></div>
            <div className="absolute left-[11px] top-3 bottom-0 w-0.5 border-l border-dashed border-slate-800"></div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Step 1: Input Query</div>
            <div className="text-slate-300 font-medium italic mt-0.5">"{question}"</div>
          </div>

          {/* STEP 2: REASONING */}
          <div className="relative pl-6 pb-2">
            <div className="absolute left-2 top-1 w-2 h-2 rounded-full bg-brand-500"></div>
            <div className="absolute left-[11px] top-3 bottom-0 w-0.5 border-l border-dashed border-slate-800"></div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Step 2: Agent Reasoning</div>
            <div className="mt-1.5 space-y-1.5">
              {reasoningSteps.map((step, idx) => (
                <div key={idx} className="flex items-start gap-2 text-slate-300">
                  <CheckCircle2 className="w-3.5 h-3.5 text-brand-400 mt-0.5 shrink-0" />
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>

          {/* STEP 3: TOOL CALLS */}
          <div className="relative pl-6 pb-1">
            <div className="absolute left-2 top-1 w-2 h-2 rounded-full bg-amber-500"></div>
            <div className="absolute left-[11px] top-3 bottom-0 w-0.5 border-l border-dashed border-slate-800"></div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Step 3: Tool Execution</div>
            {toolCalls.length === 0 ? (
              <div className="text-slate-400 mt-1 italic">No tools required for this turn. Answer retrieved directly from memory.</div>
            ) : (
              <div className="mt-2 space-y-2.5">
                {toolCalls.map((tc, idx) => (
                  <div key={idx} className="border border-slate-800 rounded bg-slate-900/40 overflow-hidden">
                    <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900 border-b border-slate-800">
                      <div className="flex items-center gap-1.5 font-mono text-[10px] text-amber-400">
                        <Wrench className="w-3 h-3" />
                        <span>{tc.tool_name}</span>
                      </div>
                      <span className={`text-[9px] px-1 rounded font-semibold uppercase ${
                        tc.status === 'success' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                      }`}>
                        {tc.status}
                      </span>
                    </div>
                    <div className="p-2 space-y-1">
                      <div className="font-mono text-[11px] text-slate-300 bg-slate-950 p-1.5 rounded overflow-x-auto">
                        <span className="text-slate-500">args:</span> {JSON.stringify(tc.tool_input)}
                      </div>
                      <div className="font-mono text-[11px] text-slate-400 bg-slate-950/60 p-1.5 rounded overflow-x-auto">
                        <span className="text-slate-500">result:</span> {formatToolOutput(tc.tool_output)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* STEP 4: FINAL RESPONSE OUTLINE */}
          <div className="relative pl-6">
            <div className="absolute left-2 top-1 w-2 h-2 rounded-full bg-emerald-500"></div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-sans">Step 4: Final Synthesis</div>
            <div className="text-slate-400 mt-0.5">Translating raw tools output into consumer-friendly response.</div>
          </div>

        </div>
      )}

      {/* ALWAYS VISIBLE FINAL RESPONSE */}
      <div className="p-4 bg-slate-900/25 border-t border-slate-800">
        <div className="text-slate-200 leading-relaxed font-sans text-sm whitespace-pre-line">
          {finalAnswer}
        </div>
      </div>
    </div>
  );
};
