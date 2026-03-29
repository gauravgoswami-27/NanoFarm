import { useState, useRef, useEffect } from 'react';

// Format simple markdown into HTML safely
const formatMessage = (text) => {
  if (!text) return { __html: '' };
  let formatted = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
  formatted = formatted.replace(/\\n/g, '<br/>');
  return { __html: formatted };
};

function AIExpertChat({ webhookUrl }) {
  const [messages, setMessages] = useState([
    { id: '1', sender: 'system', text: "Hello! I'm your AI Agronomist. How can I help you today?" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatHistoryRef = useRef(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || !webhookUrl) return;

    // Add user message
    const userMsg = { id: Date.now().toString(), sender: 'user', text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chatInput: text, message: text })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      let botText = "Sorry, I couldn't understand the response.";
      if (result.status === 'success' && result.type === 'chatbot_response') {
        botText = result.data.chatbot_response;
      } else if (result.status === 'error') {
        botText = `Error: ${result.message}`;
      } else {
        botText = JSON.stringify(result);
      }

      setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'system', text: botText }]);
    } catch (err) {
      setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'system', text: `Connection error: ${err.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="tab-content chat-tab-container">
      <h2>AI Agronomist Chat</h2>
      <p className="tab-description">Ask any farming, agriculture, or crop-related questions.</p>
      
      <div className="chat-container">
        <div className="chat-history" ref={chatHistoryRef}>
          {messages.map(msg => (
            <div key={msg.id} className={`message ${msg.sender}-message`}>
              <div className="avatar">{msg.sender === 'user' ? '👤' : '🌿'}</div>
              <div className="bubble" dangerouslySetInnerHTML={formatMessage(msg.text)} />
            </div>
          ))}
          {isLoading && (
            <div className="message system-message">
              <div className="avatar">🌿</div>
              <div className="bubble">
                <span style={{ 
                  display: 'inline-block', 
                  animation: 'pulse 1.5s infinite',
                  letterSpacing: '2px'
                }}>...</span>
              </div>
            </div>
          )}
        </div>
        
        <form onSubmit={handleSubmit} className="chat-input-area">
          <input 
            type="text" 
            placeholder="e.g., When is the best time to plant wheat?..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!webhookUrl || isLoading}
            required 
            autoComplete="off"
          />
          <button type="submit" className="send-btn" disabled={!webhookUrl || isLoading || !input.trim()}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </form>
      </div>

      <style dangerouslySetInnerHTML={{__html: `
        @keyframes pulse {
          0% { opacity: 0.5; }
          50% { opacity: 1; }
          100% { opacity: 0.5; }
        }
      `}} />
    </div>
  );
}

export default AIExpertChat;
