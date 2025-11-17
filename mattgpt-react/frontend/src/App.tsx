import { useState, useEffect, useRef } from 'react';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import ThinkingIndicator from './components/ThinkingIndicator';
import { askQuestion, Source } from './services/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

const SUGGESTION_CHIPS = [
  "How did Matt scale engineering teams?",
  "Show me agile transformation examples",
  "What's Matt's experience with payments?",
  "Tell me about digital transformation at banks",
  "How does Matt approach stakeholder management?",
  "What methodologies has Matt used in practice?"
];

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsThinking(true);

    try {
      // Call API
      const response = await askQuestion(content);

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Sorry, I encountered an error processing your question. Please try again.",
        sources: [],
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsThinking(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="min-h-screen bg-gray-bg flex flex-col">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-primary to-purple-600 text-white py-6 px-4 shadow-md">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="text-3xl">🐾</div>
            <div>
              <h1 className="text-2xl font-bold">MattGPT</h1>
              <p className="text-purple-100 text-sm">Ask Agy about Matt's 20+ years of experience</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto pb-32">
        <div className="max-w-3xl mx-auto px-4 py-8">
          {isEmpty ? (
            // Landing page (empty state)
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
              <div className="text-6xl mb-6">🐾</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Hi, I'm Agy!
              </h2>
              <p className="text-gray-600 text-center mb-8 max-w-md">
                I can help you explore Matt Pugmire's portfolio of 115+ transformation projects.
                Try asking about his experience:
              </p>

              {/* Suggestion chips */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl mb-8">
                {SUGGESTION_CHIPS.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="p-4 bg-white border-2 border-gray-border rounded-lg text-left hover:border-purple-primary hover:bg-purple-50 transition-all text-sm font-medium text-gray-700"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            // Conversation view
            <div>
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  role={message.role}
                  content={message.content}
                  sources={message.sources}
                />
              ))}
              {isThinking && <ThinkingIndicator />}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>

      {/* Sticky input at bottom */}
      <ChatInput onSend={handleSendMessage} disabled={isThinking} />
    </div>
  );
}

export default App;
