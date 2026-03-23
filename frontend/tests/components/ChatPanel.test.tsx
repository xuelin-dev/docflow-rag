import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ChatPanel from '../../src/components/chat/ChatPanel';

describe('ChatPanel', () => {
  it('renders empty state when no conversation provided', () => {
    render(<ChatPanel />);
    expect(screen.getByText(/select a conversation/i)).toBeInTheDocument();
  });

  it('renders conversation messages when provided', () => {
    const mockConversation = {
      id: 'test-1',
      title: 'Test Chat',
      namespace: 'default',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      messages: [
        {
          id: 'msg-1',
          role: 'user' as const,
          content: 'Hello',
          timestamp: new Date().toISOString(),
        },
        {
          id: 'msg-2',
          role: 'assistant' as const,
          content: 'Hi there!',
          timestamp: new Date().toISOString(),
          sources: [],
        },
      ],
    };

    render(<ChatPanel conversation={mockConversation} />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });
});
