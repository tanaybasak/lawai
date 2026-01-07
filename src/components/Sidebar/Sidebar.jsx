import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faTrash, faMessage, faPen, faCheck, faTimes } from '@fortawesome/free-solid-svg-icons';
import styles from './Sidebar.module.scss';
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
      <div className={styles.sidebarHeader}>
        <button className={styles.newChatBtn} onClick={onNewChat}>
          <FontAwesomeIcon icon={faPlus} />
          <span>{t('chat.new_chat')}</span>
        </button>
      </div>

      <div className={styles.chatList}>
        {chats.length === 0 ? (
          <div className={styles.emptyState}>
            <p>{t('chat.no_chats')}</p>
            <p className={styles.emptyHint}>{t('chat.start_conversation')}</p>
          </div>
        ) : (
          chats
            .filter((chat) => chat.messages.length > 0)
            .map((chat) => (
            <div
              key={chat.id}
              className={`${styles.chatItem} ${
                chat.id === activeChatId ? styles.active : ''
              }`}
              onClick={() => onSelectChat(chat.id)}
            >
              <div className={styles.chatItemContent}>
                <div className={styles.chatIcon}>
                  <FontAwesomeIcon icon={faMessage} />
                </div>
                <div className={styles.chatDetails}>
                  {editingChatId === chat.id ? (
                    <div className={styles.chatTitleEdit}>
                      <input
                        type="text"
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleRenameSubmit(e, chat.id);
                          if (e.key === 'Escape') handleRenameCancel(e);
                        }}
                        className={styles.titleInput}
                        autoFocus
                      />
                      <button
                        className={styles.renameConfirmBtn}
                        onClick={(e) => handleRenameSubmit(e, chat.id)}
                        title="Save"
                      >
                        <FontAwesomeIcon icon={faCheck} />
                      </button>
                      <button
                        className={styles.renameCancelBtn}
                        onClick={handleRenameCancel}
                        title="Cancel"
                      >
                        <FontAwesomeIcon icon={faTimes} />
                      </button>
                    </div>
                  ) : (
                    <div className={styles.chatTitle}>{chat.title}</div>
                  )}
                  <div className={styles.chatPreview}>
                    {chat.messages.length > 0
                      ? chat.messages[0].message.substring(0, 50) + '...'
                      : t('chat.no_messages')}
                  </div>
                  <div className={styles.chatMeta}>
                    <span className={styles.chatDate}>
                      {formatChatDate(chat.updatedAt)}
                    </span>
                  </div>
                </div>
                <div className={styles.chatActions}>
                  {editingChatId !== chat.id && (
                    <button
                      className={styles.renameBtn}
                      onClick={(e) => handleRenameClick(e, chat)}
                      title="Rename chat"
                    >
                      <FontAwesomeIcon icon={faPen} />
                    </button>
                  )}
                  {chats.filter(c => c.messages.length > 0).length > 1 && editingChatId !== chat.id && (
                    <button
                      className={`${styles.deleteBtn} ${
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

      <div className={styles.sidebarFooter}>
        <div className={styles.chatCount}>
          {chats.length} {t('chat.chats', { count: chats.length })}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
