import { useParams } from 'react-router-dom';
import { useChatStore } from '../stores/chatStore';
import ChatPanel from '../components/chat/ChatPanel';
import SourcePanel from '../components/chat/SourcePanel';

export default function ChatPage() {
  const { conversationId } = useParams();
  const { conversations, activeConversationId, setActiveConversation, createConversation } = useChatStore();

  const activeConversation = conversations.find(c => c.id === (conversationId || activeConversationId));

  return (
    <div className="flex h-full">
      {/* Left Sidebar - Conversation List */}
      <div className="w-64 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={createConversation}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            New Chat
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {conversations.map(conv => (
            <div
              key={conv.id}
              onClick={() => setActiveConversation(conv.id)}
              className={`p-4 cursor-pointer border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 ${
                conv.id === activeConversationId ? 'bg-gray-100 dark:bg-gray-800' : ''
              }`}
            >
              <div className="font-medium truncate">{conv.title || 'New Conversation'}</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {new Date(conv.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Center - Chat Panel */}
      <div className="flex-1 flex flex-col">
        <ChatPanel conversation={activeConversation} />
      </div>

      {/* Right - Source Panel */}
      <div className="w-96 border-l border-gray-200 dark:border-gray-700">
        <SourcePanel sources={activeConversation?.messages[activeConversation.messages.length - 1]?.sources || []} />
      </div>
    </div>
  );
}
