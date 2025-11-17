import { Source } from '../services/api';

interface SourceCardProps {
  source: Source;
}

export default function SourceCard({ source }: SourceCardProps) {
  return (
    <div className="p-3 bg-gray-50 border border-gray-border rounded-lg hover:border-purple-primary transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-gray-900 truncate">
            {source.title}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {source.client}
          </div>
        </div>
        {source.score && (
          <div className="flex-shrink-0 text-xs text-gray-400">
            {Math.round(source.score * 100)}%
          </div>
        )}
      </div>
      <a
        href="#"
        className="inline-flex items-center gap-1 mt-2 text-xs font-medium text-purple-primary hover:text-purple-600"
        onClick={(e) => {
          e.preventDefault();
          // TODO: Implement source detail modal/navigation
          console.log('View source:', source.id);
        }}
      >
        View details
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </a>
    </div>
  );
}
