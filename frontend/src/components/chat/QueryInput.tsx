import { useState, KeyboardEvent } from 'react';
import { useQuery } from '../hooks/useQuery';
import Button from '../ui/Button';
import { Send } from 'lucide-react';

interface QueryInputProps {
  conversationId: string;
}

export default function QueryInput({ conversationId }: QueryInputProps) {
  const [input, setInput] = useState('');
  const { sendQuery, isLoading } = useQuery();

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;
    
    await sendQuery({
      query: input,
      conversation_id: conversationId,
    });
    
    setInput('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex gap-2">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question... (Ctrl+Enter to send)"
        disabled={isLoading}
        className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        rows={3}
      />
      <Button
        onClick={handleSubmit}
        disabled={!input.trim() || isLoading}
        className="self-end"
      >
        <Send className="w-5 h-5" />
      </Button>
    </div>
  );
}
