import { useRef, useEffect } from 'react';
import { Conversation } from '../../lib/types';
import MessageBubble from './MessageBubble';
import QueryInput from './QueryInput';

interface ChatPanelProps {
  conversation?: Conversation;
}

export default function ChatPanel({ conversation }: ChatPanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  if (!conversation) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
        Select a conversation or start a new one
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {conversation.messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="border-t border-gray-200 dark:border-gray-700 p-4">
        <QueryInput conversationId={conversation.id} />
      </div>
    </div>
  );
}
