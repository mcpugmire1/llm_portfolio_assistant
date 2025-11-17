/**
 * API service for MattGPT backend
 */

export interface Source {
  id: string;
  title: string;
  client: string;
  score?: number;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
  isNonsense: boolean;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001';

export async function askQuestion(query: string): Promise<AskResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error asking question:', error);
    throw error;
  }
}
