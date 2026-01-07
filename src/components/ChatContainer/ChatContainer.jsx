import React from 'react';
import styles from './ChatContainer.module.scss';
import AgentMessage from '../AgentMessage/AgentMessage';
import MessageBubble from '../MessageBubble/MessageBubble';

const ChatContainer = ({ messages, isLoading }) => {
  return (
    <div className={styles['chat-container']}>
      <div className={styles['messages-list']}>
        {messages.map((msg, index) => {
          if (msg.type === 'agent') {
            return (
              <AgentMessage
                key={index}
                agentName={msg.agentName}
                message={msg.message}
                agentType={msg.agentType}
                isTyping={msg.isTyping}
              />
            );
          } else {
            return (
              <MessageBubble
                key={index}
                message={msg.message}
                isUser={msg.isUser}
              />
            );
          }
        })}
        
        {isLoading && (
          <div className={styles.loadingIndicator}>
            <div className={styles.loadingDot}></div>
            <div className={styles.loadingDot}></div>
            <div className={styles.loadingDot}></div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatContainer;
