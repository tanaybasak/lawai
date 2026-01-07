// Chat utility functions for managing multiple chat sessions

/**
 * Generate a unique chat ID
 */
export const generateChatId = () => {
  return `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Generate a chat title from the first user message
 * @param {string} message - The first user message
 * @returns {string} - Generated title (max 50 chars)
 */
export const generateChatTitle = (message) => {
  if (!message) return 'New Chat';
  
  // Clean and truncate message
  let title = message.trim();
  
  // Remove common question words for cleaner titles
  title = title.replace(/^(what is|what are|tell me about|explain|how to|can you)/i, '').trim();
  
  // Capitalize first letter
  title = title.charAt(0).toUpperCase() + title.slice(1);
  
  // Truncate to 50 chars
  if (title.length > 50) {
    title = title.substring(0, 47) + '...';
  }
  
  return title || 'New Chat';
};

/**
 * Create a new empty chat object
 * @param {string} title - Optional chat title
 * @returns {object} - New chat object
 */
export const createNewChat = (title = 'New Chat') => {
  const now = Date.now();
  return {
    id: generateChatId(),
    title: title,
    messages: [],
    createdAt: now,
    updatedAt: now
  };
};

/**
 * Sort chats by most recently updated
 */
export const sortChatsByDate = (chats) => {
  return Object.values(chats).sort((a, b) => b.updatedAt - a.updatedAt);
};

/**
 * Save chats to localStorage
 */
export const saveChatsToStorage = (chats, activeChatId) => {
  try {
    localStorage.setItem('lawai_chats', JSON.stringify(chats));
    localStorage.setItem('lawai_active_chat', activeChatId);
  } catch (error) {
    console.error('Error saving chats to localStorage:', error);
    // Handle quota exceeded error
    if (error.name === 'QuotaExceededError') {
      // Could implement cleanup of old chats here
      alert('Storage limit reached. Please delete some old chats.');
    }
  }
};

/**
 * Load chats from localStorage
 */
export const loadChatsFromStorage = () => {
  try {
    const chatsJson = localStorage.getItem('lawai_chats');
    const activeChatId = localStorage.getItem('lawai_active_chat');
    
    if (chatsJson) {
      const chats = JSON.parse(chatsJson);
      return { chats, activeChatId };
    }
  } catch (error) {
    console.error('Error loading chats from localStorage:', error);
  }
  
  // Return default state if nothing in storage
  const defaultChat = createNewChat();
  return {
    chats: { [defaultChat.id]: defaultChat },
    activeChatId: defaultChat.id
  };
};

/**
 * Delete old chats if limit exceeded
 */
export const enforceChatsLimit = (chats, maxChats = 50) => {
  const chatArray = sortChatsByDate(chats);
  
  if (chatArray.length <= maxChats) {
    return chats;
  }
  
  // Keep only the most recent maxChats
  const chatsToKeep = chatArray.slice(0, maxChats);
  const newChats = {};
  
  chatsToKeep.forEach(chat => {
    newChats[chat.id] = chat;
  });
  
  return newChats;
};

/**
 * Format date for display
 */
export const formatChatDate = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString();
};
