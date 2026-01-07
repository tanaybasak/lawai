import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faTrash, faMessage, faPen, faCheck, faTimes } from '@fortawesome/free-solid-svg-icons';
import styles from './Sidebar.module.css';
import { formatChatDate } from '../../utils/chatUtils';

const Sidebar = ({ chats, activeChatId, onSelectChat, onNewChat, onDeleteChat, onRenameChat, isOpen, onToggle }) => {
  const { t } = useTranslation();
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [editingChatId, setEditingChatId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');

  const handleDeleteClick = (e, chatId) => {
    e.stopPropagation();
    if (deleteConfirm === chatId) {
      onDeleteChat(chatId);
      setDeleteConfirm(null);
    } else {
      setDeleteConfirm(chatId);
      // Auto-cancel after 3 seconds
      setTimeout(() => setDeleteConfirm(null), 3000);
    }
  };

  const handleRenameClick = (e, chat) => {
    e.stopPropagation();
    setEditingChatId(chat.id);
    setEditingTitle(chat.title);
  };

  const handleRenameSubmit = (e, chatId) => {
    e.stopPropagation();
    if (editingTitle.trim()) {
      onRenameChat(chatId, editingTitle.trim());
    }
    setEditingChatId(null);
    setEditingTitle('');
  };

  const handleRenameCancel = (e) => {
    e.stopPropagation();
    setEditingChatId(null);
    setEditingTitle('');
  };

  return (
    <div className={`${styles.sidebar} ${isOpen ? styles.open : ''}`}>
      <div className={styles['sidebar-header']}>
        <button className={styles['new-chat-btn']} onClick={onNewChat}>
          <FontAwesomeIcon icon={faPlus} />
          <span>{t('chat.new_chat')}</span>
        </button>
      </div>

      <div className={styles['chat-list']}>
        {chats.length === 0 ? (
          <div className={styles['empty-state']}>
            <p>{t('chat.no_chats')}</p>
            <p className={styles['empty-hint']}>{t('chat.start_conversation')}</p>
          </div>
        ) : (
          chats
            .filter((chat) => chat.messages.length > 0)
            .map((chat) => (
            <div
              key={chat.id}
              className={`${styles['chat-item']} ${
                chat.id === activeChatId ? styles.active : ''
              }`}
              onClick={() => onSelectChat(chat.id)}
            >
              <div className={styles['chat-item-content']}>
                <div className={styles['chat-icon']}>
                  <FontAwesomeIcon icon={faMessage} />
                </div>
                <div className={styles['chat-details']}>
                  {editingChatId === chat.id ? (
                    <div className={styles['chat-title-edit']}>
                      <input
                        type="text"
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleRenameSubmit(e, chat.id);
                          if (e.key === 'Escape') handleRenameCancel(e);
                        }}
                        className={styles['title-input']}
                        autoFocus
                      />
                      <button
                        className={styles['rename-confirm-btn']}
                        onClick={(e) => handleRenameSubmit(e, chat.id)}
                        title="Save"
                      >
                        <FontAwesomeIcon icon={faCheck} />
                      </button>
                      <button
                        className={styles['rename-cancel-btn']}
                        onClick={handleRenameCancel}
                        title="Cancel"
                      >
                        <FontAwesomeIcon icon={faTimes} />
                      </button>
                    </div>
                  ) : (
                    <div className={styles['chat-title']}>{chat.title}</div>
                  )}
                  <div className={styles['chat-preview']}>
                    {chat.messages.length > 0
                      ? chat.messages[0].message.substring(0, 50) + '...'
                      : t('chat.no_messages')}
                  </div>
                  <div className={styles['chat-meta']}>
                    <span className={styles['chat-date']}>
                      {formatChatDate(chat.updatedAt)}
                    </span>
                    {chat.messages.length > 0 && (
                      <span className={styles['message-count']}>
                        {chat.messages.length} {t('chat.messages', { count: chat.messages.length })}
                      </span>
                    )}
                  </div>
                </div>
                <div className={styles['chat-actions']}>
                  {editingChatId !== chat.id && (
                    <button
                      className={styles['rename-btn']}
                      onClick={(e) => handleRenameClick(e, chat)}
                      title="Rename chat"
                    >
                      <FontAwesomeIcon icon={faPen} />
                    </button>
                  )}
                  {chats.filter(c => c.messages.length > 0).length > 1 && editingChatId !== chat.id && (
                    <button
                      className={`${styles['delete-btn']} ${
                        deleteConfirm === chat.id ? styles.confirm : ''
                      }`}
                      onClick={(e) => handleDeleteClick(e, chat.id)}
                      title={deleteConfirm === chat.id ? t('chat.delete_confirm') : t('chat.delete_chat')}
                    >
                      <FontAwesomeIcon icon={faTrash} />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className={styles['sidebar-footer']}>
        <div className={styles['chat-count']}>
          {chats.length} {t('chat.chats', { count: chats.length })}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
