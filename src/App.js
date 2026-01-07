import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faParagraph, 
  faSpellCheck, 
  faRobot, 
  faShieldAlt, 
  faUserCheck, 
  faComments, 
  faImage, 
  faLanguage, 
  faFileAlt,
  faEllipsisH,
  faGlobe
} from '@fortawesome/free-solid-svg-icons';
import styles from './App.module.css';
import EmptyState from './components/EmptyState/EmptyState';
import ChatContainer from './components/ChatContainer/ChatContainer';
import InputBar from './components/InputBar/InputBar';
import Sidebar from './components/Sidebar/Sidebar';
import Header from './components/Header/Header';
import { legalAPI } from './services/api';
import { 
  loadChatsFromStorage, 
  saveChatsToStorage, 
  createNewChat,
  generateChatTitle,
  sortChatsByDate,
  enforceChatsLimit
} from './utils/chatUtils';

function App() {
  const [chats, setChats] = useState({});
  const [activeChatId, setActiveChatId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('checking');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    // Load chats from localStorage and check API health
    const { chats: loadedChats, activeChatId: loadedActiveChatId } = loadChatsFromStorage();
    setChats(loadedChats);
    setActiveChatId(loadedActiveChatId);
    checkAPIHealth();
  }, []);

  // Save to localStorage whenever chats change
  useEffect(() => {
    if (Object.keys(chats).length > 0 && activeChatId) {
      saveChatsToStorage(chats, activeChatId);
    }
  }, [chats, activeChatId]);

  const checkAPIHealth = async () => {
    try {
      await legalAPI.healthCheck();
      setApiStatus('connected');
    } catch (error) {
      console.error('API health check failed:', error);
      setApiStatus('disconnected');
    }
  };

  const handleNewChat = () => {
    // Check if current chat is empty, if so, just use it instead of creating new one
    const currentChat = getCurrentChat();
    if (currentChat && currentChat.messages.length === 0) {
      setIsSidebarOpen(false);
      return;
    }
    
    const newChat = createNewChat();
    setChats(prev => enforceChatsLimit({ ...prev, [newChat.id]: newChat }));
    setActiveChatId(newChat.id);
    setIsSidebarOpen(false);
  };

  const handleSelectChat = (chatId) => {
    setActiveChatId(chatId);
    setIsSidebarOpen(false);
  };

  const handleDeleteChat = (chatId) => {
    const chatIds = Object.keys(chats);
    
    // Don't delete if it's the only chat
    if (chatIds.length === 1) {
      return;
    }
    
    const newChats = { ...chats };
    delete newChats[chatId];
    setChats(newChats);
    
    // If deleting active chat, switch to another
    if (chatId === activeChatId) {
      const remainingIds = Object.keys(newChats);
      setActiveChatId(remainingIds[0]);
    }
  };

  const handleRenameChat = (chatId, newTitle) => {
    setChats(prev => ({
      ...prev,
      [chatId]: {
        ...prev[chatId],
        title: newTitle,
        updatedAt: Date.now()
      }
    }));
  };

  const getCurrentChat = () => {
    return chats[activeChatId] || null;
  };

  const updateCurrentChat = (updates) => {
    if (!activeChatId) return;
    
    setChats(prev => ({
      ...prev,
      [activeChatId]: {
        ...prev[activeChatId],
        ...updates,
        updatedAt: Date.now()
      }
    }));
  };

  const handleSubmit = async (message) => {
    if (!activeChatId) return;
    
    const currentChat = getCurrentChat();
    
    // Add user message
    const userMessage = {
      type: 'message',
      message: message,
      isUser: true
    };
    
    const newMessages = [...currentChat.messages, userMessage];
    updateCurrentChat({ messages: newMessages });
    
    // Auto-generate title from first message
    if (currentChat.messages.length === 0) {
      const newTitle = generateChatTitle(message);
      updateCurrentChat({ title: newTitle });
    }
    
    setIsLoading(true);

    // Add a placeholder AI message that will be updated with streaming content
    const aiMessageId = `ai-${Date.now()}`;
    const aiMessage = {
      id: aiMessageId,
      type: 'agent',
      agentName: 'Legal Assistant',
      agentType: 'strategist',
      message: ''
    };
    
    updateCurrentChat({ messages: [...newMessages, aiMessage] });

    try {
      // Get chat history for context
      const chatHistory = currentChat.messages
        .filter(msg => msg.type === 'message' || msg.type === 'agent')
        .map(msg => ({
          role: msg.isUser || msg.type === 'message' ? 'user' : 'assistant',
          content: msg.message
        }));
      
      // Call streaming API
      const response = await fetch('http://localhost:8000/query-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: message,
          chat_history: chatHistory
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            if (data === '[DONE]') {
              break;
            }

            try {
              const parsed = JSON.parse(data);
              
              if (parsed.type === 'content') {
                accumulatedText += parsed.content;
                
                // Update the AI message with accumulated text
                // eslint-disable-next-line no-loop-func
                setChats(prev => {
                  const chat = prev[activeChatId];
                  const messages = chat.messages.map(msg => 
                    msg.id === aiMessageId 
                      ? { ...msg, message: accumulatedText }
                      : msg
                  );
                  return {
                    ...prev,
                    [activeChatId]: {
                      ...chat,
                      messages,
                      updatedAt: Date.now()
                    }
                  };
                });
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
      
    } catch (error) {
      console.error('Error querying legal assistant:', error);
      
      // Update the AI message with error
      setChats(prev => {
        const chat = prev[activeChatId];
        const messages = chat.messages.map(msg => 
          msg.id === aiMessageId 
            ? { 
                ...msg, 
                message: 'Sorry, I encountered an error. Please make sure the backend server is running.',
                agentName: 'System',
                agentType: 'designer'
              }
            : msg
        );
        return {
          ...prev,
          [activeChatId]: {
            ...chat,
            messages,
            updatedAt: Date.now()
          }
        };
      });
    } finally {
      setIsLoading(false);
    }
  };

  const currentChat = getCurrentChat();
  const chatList = sortChatsByDate(chats);

  return (
    <div className={styles.app}>
      <div className={styles.sidebar}>
        <div className={styles.logo}>
          <div className={styles['logo-icon']}>
            <img 
              src="https://sspark.genspark.ai/cfimages?u1=qRqawqrDk00RQMP6wXEUHuxWslNIbEJeCgy3Kqs9GXjw0sIL8483WOde5qmLhtDY%2Fhw0V%2BGoiSSXpfCp3EeKCA2VGgjvltWHVtZrtmfw3iMJN6A6k3wj&u2=tJ5MdbAFRhq2FK3f&width=2560" 
              alt="LawAI Logo" 
            />
          </div>
        </div>
        
        <div className={styles['sidebar-divider']}></div>
        
        <div className={styles['sidebar-section']}>
          <button className={styles['sidebar-icon']}>
            <FontAwesomeIcon icon={faParagraph} />
            <span className={styles['icon-label']}>Paraphraser</span>
          </button>
          
          <button className={styles['sidebar-icon']}>
            <FontAwesomeIcon icon={faSpellCheck} />
            <span className={styles['icon-label']}>Grammar Checker</span>
          </button>
          
          <button className={styles['sidebar-icon']}>
            <FontAwesomeIcon icon={faRobot} />
            <span className={styles['icon-label']}>AI Detector</span>
          </button>
          
          <button className={styles['sidebar-icon']}>
            <FontAwesomeIcon icon={faShieldAlt} />
            <span className={styles['icon-label']}>Plagiarism Checker</span>
          </button>
          
          <button className={styles['sidebar-icon']}>
            <FontAwesomeIcon icon={faUserCheck} />
            <span className={styles['icon-label']}>AI Humanizer</span>
          </button>
          
          <button className={`${styles['sidebar-icon']} ${styles.active}`}>
            <FontAwesomeIcon icon={faComments} />
            <span className={styles['icon-label']}>Legal AI Chat</span>
          </button>
          
          <button className={styles['sidebar-icon']}>
            <FontAwesomeIcon icon={faImage} />
            <span className={styles['icon-label']}>AI Image Generator</span>
          </button>
          
          <button className={styles['sidebar-icon']}>
            <FontAwesomeIcon icon={faLanguage} />
            <span className={styles['icon-label']}>Translate</span>
          </button>
          
          <button className={styles['sidebar-icon']}>
            <FontAwesomeIcon icon={faFileAlt} />
            <span className={styles['icon-label']}>Summarizer</span>
          </button>
        </div>
        
        <div className={styles['sidebar-bottom']}>
          <button className={styles['sidebar-icon']}>
            <FontAwesomeIcon icon={faEllipsisH} />
            <span className={styles['icon-label']}>More</span>
          </button>
          
          <div className={styles['sidebar-divider']}></div>
          
          <button className={styles['sidebar-icon']}>
            <FontAwesomeIcon icon={faGlobe} />
            <span className={styles['icon-label']}>LawAI for Chrome</span>
          </button>
        </div>
      </div>

      <Sidebar
        chats={chatList}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        onRenameChat={handleRenameChat}
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
      />
      
      <div className={styles.content}>
        <Header 
          title={currentChat?.title || 'LawAI Assistant'} 
          onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)}
          onNewChat={handleNewChat}
        />

        {apiStatus === 'disconnected' && (
          <div className={styles.apiWarning}>
            ⚠️ Backend server is not connected. Please start the server.
          </div>
        )}
        
        {currentChat && currentChat.messages.length === 0 ? (
          <EmptyState onSubmit={handleSubmit} />
        ) : (
          <div className={styles.chatWrapper}>
            <ChatContainer messages={currentChat?.messages || []} isLoading={isLoading} />
            <InputBar onSendMessage={handleSubmit} disabled={isLoading} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
