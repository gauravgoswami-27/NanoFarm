import { useState, useRef, useEffect } from 'react';

const WELCOME = {
  id: 'welcome',
  sender: 'system',
  text: "Hello! I'm nanoBot, your AI agronomist 🌿\n\nAsk me anything about farming — crop diseases, planting season, soil management, pest control, or irrigation tips. I'm here to help!",
};

// Simple markdown parser: **bold**, newlines, bullet points
function parseMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul style="margin: 8px 0 8px 16px; display:flex; flex-direction:column; gap:4px;">$1</ul>')
    .replace(/\n/g, '<br/>');
}

function AIExpertChat({ sendChat }) {
  const [messages,  setMessages]  = useState([WELCOME]);
  const [input,     setInput]     = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef  = useRef(null);
  const inputRef   = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isLoading) return;

    const userMsg = { id: Date.now().toString(), sender: 'user', text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      // Format history for the backend
      const history = messages.map(m => ({
        role: m.sender === 'user' ? 'user' : 'model',
        parts: m.text
      }));

      const reply = await sendChat(text, history);
      setMessages(prev => [
        ...prev,
        { id: (Date.now() + 1).toString(), sender: 'system', text: reply },
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'system',
          text: `⚠️ Connection error: ${err.message}\n\nPlease check that the n8n webhook is configured in your .env file.`,
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const SUGGESTIONS = [
    'When should I plant wheat?',
    'How to treat rice brown spot?',
    'Best fertilizer for cotton?',
  ];

  return (
    <div className="chat-page">
      {/* Header */}
      <div className="page-header" style={{ marginBottom: '1rem' }}>
        <div className="page-header-top">
          <div className="page-icon" style={{ background: '#dbeafe' }}>💬</div>
          <h2>AI Agronomist</h2>
        </div>
        <p>Ask any farming or crop question in plain language.</p>
      </div>

      {/* Suggestion chips — only when no user messages yet */}
      {messages.length === 1 && (
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '1rem' }}>
          {SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              onClick={() => { setInput(s); inputRef.current?.focus(); }}
              style={{
                padding: '8px 14px',
                background: 'white',
                border: '1.5px solid var(--border-strong)',
                borderRadius: '100px',
                font: '600 0.83rem/1 inherit',
                color: 'var(--green-700)',
                cursor: 'pointer',
                transition: 'var(--transition)',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'var(--green-50)'; e.currentTarget.style.borderColor = 'var(--green-400)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'white'; e.currentTarget.style.borderColor = ''; }}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Chat Window */}
      <div className="chat-window">
        <div className="chat-messages" id="chat-messages">
          {messages.map(msg => (
            <div key={msg.id} className={`chat-msg ${msg.sender}`}>
              <div className="chat-avatar">
                {msg.sender === 'user' ? '👤' : '🌿'}
              </div>
              <div
                className="chat-bubble"
                dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.text) }}
              />
            </div>
          ))}

          {isLoading && (
            <div className="chat-msg system">
              <div className="chat-avatar">🌿</div>
              <div className="chat-bubble">
                <div className="chat-typing">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input Bar */}
        <form className="chat-input-bar" onSubmit={handleSubmit} id="chat-form">
          <input
            ref={inputRef}
            type="text"
            placeholder="Ask about crops, diseases, soil management…"
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={isLoading}
            autoComplete="off"
            id="chat-input"
          />
          <button
            type="submit"
            className="chat-send-btn"
            disabled={isLoading || !input.trim()}
            id="chat-send-btn"
            aria-label="Send message"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}

export default AIExpertChat;
