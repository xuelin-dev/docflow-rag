import { Message } from '../../lib/types';
import { User, Bot } from 'lucide-react';
import StreamingText from './StreamingText';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}
      
      <div
        className={`max-w-2xl rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
        }`}
      >
        {message.streaming ? (
          <StreamingText text={message.content} />
        ) : (
          <div className="prose dark:prose-invert max-w-none">
            {message.content}
          </div>
        )}
        
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
              Sources ({message.sources.length})
            </div>
            <div className="flex flex-wrap gap-2">
              {message.sources.slice(0, 3).map((source, idx) => (
                <div
                  key={idx}
                  className="text-xs bg-white dark:bg-gray-700 px-2 py-1 rounded border border-gray-200 dark:border-gray-600"
                >
                  {source.document_name} • {source.score.toFixed(2)}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
}
