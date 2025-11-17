export default function ThinkingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex flex-row gap-3 max-w-[80%]">
        {/* Agy Avatar */}
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-purple-primary flex items-center justify-center text-white text-sm animate-pulse">
            🐾
          </div>
        </div>

        {/* Thinking animation */}
        <div className="flex-1">
          <div className="p-4 rounded-lg bg-white border border-gray-border">
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-purple-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-purple-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-purple-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="text-sm text-gray-500">Agy is thinking...</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
