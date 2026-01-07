import React from 'react';
import styles from './MessageBubble.module.scss';

const MessageBubble = ({ message, isUser }) => {
  return (
    <div className={`${styles.messageBubble} ${isUser ? styles.user : styles.agent}`}>
      <p className={styles.messageText}>{message}</p>
    </div>
  );
};

export default MessageBubble;
