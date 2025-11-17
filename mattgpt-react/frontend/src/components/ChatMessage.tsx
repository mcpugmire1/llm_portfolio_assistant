import { Source } from '../services/api';
import SourceCard from './SourceCard';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

export default function ChatMessage({ role, content, sources }: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-3 max-w-[80%]`}>
        {/* Avatar */}
        <div className="flex-shrink-0">
          {isUser ? (
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium">
              U
            </div>
          ) : (
            <div className="w-8 h-8 rounded-full bg-purple-primary flex items-center justify-center text-white text-sm">
              🐾
            </div>
          )}
        </div>

        {/* Message content */}
        <div className="flex-1">
          <div
            className={`p-4 rounded-lg ${
              isUser
                ? 'bg-blue-light text-gray-900'
                : 'bg-white text-gray-900 border border-gray-border'
            }`}
          >
            <div className="whitespace-pre-wrap">{content}</div>
          </div>

          {/* Sources */}
          {!isUser && sources && sources.length > 0 && (
            <div className="mt-3 space-y-2">
              <div className="text-xs text-gray-500 font-medium">Sources:</div>
              <div className="grid grid-cols-1 gap-2">
                {sources.slice(0, 3).map((source) => (
                  <SourceCard key={source.id} source={source} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
