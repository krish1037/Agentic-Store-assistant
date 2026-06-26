import type { ChatResponse, HistoryResponse } from '../types/chat';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

export async function sendMessage(message: string, sessionId: string): Promise<ChatResponse> {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.response || `Server returned ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

export async function getHistory(sessionId: string): Promise<HistoryResponse> {
  const response = await fetch(`${BASE_URL}/history/${sessionId}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch history: ${response.statusText}`);
  }

  return response.json();
}
