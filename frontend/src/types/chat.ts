export interface ToolCallRecord {
  tool_name: string;
  tool_input: Record<string, any>;
  tool_output: any;
  status: 'success' | 'error';
}

export interface ChatResponse {
  response: string;
  session_id: string;
  reasoning_steps: string[];
  tool_calls: ToolCallRecord[];
  used_rag: boolean;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  reasoning_steps?: string[];
  tool_calls?: ToolCallRecord[];
  used_rag?: boolean;
}

export interface HistoryResponse {
  session_id: string;
  messages: ChatMessage[];
}
