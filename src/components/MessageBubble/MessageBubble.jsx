import React from 'react';
import styles from './MessageBubble.module.scss';

const MessageBubble = ({ message, isUser }) => {
  return (
    <div className={`${styles['message-bubble']} ${isUser ? styles.user : styles.agent}`}>
      <p className={styles['message-text']}>{message}</p>
    </div>
  );
};

export default MessageBubble;
