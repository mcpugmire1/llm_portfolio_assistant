import { useState, KeyboardEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="sticky bottom-0 bg-gray-bg border-t border-gray-border p-4">
      <div className="max-w-3xl mx-auto">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Agy about Matt's experience..."
            disabled={disabled}
            className="flex-1 p-3 border border-gray-border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-purple-primary focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            rows={1}
            style={{
              minHeight: '48px',
              maxHeight: '120px',
            }}
          />
          <button
            onClick={handleSend}
            disabled={disabled || !input.trim()}
            className="px-6 py-3 bg-purple-primary text-white rounded-lg font-medium hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-primary focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            Ask Agy 🐾
          </button>
        </div>
      </div>
    </div>
  );
}
