import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowRight, faPaperclip, faGear } from '@fortawesome/free-solid-svg-icons';
import styles from './EmptyState.module.scss';

const EmptyState = ({ onSubmit }) => {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState('');

  const useCases = [
    { icon: '⚖️', text: t('empty_state.draft_contracts'), color: '#10b981' },
    { icon: '📜', text: t('empty_state.research_law'), color: '#3b82f6' },
    { icon: '💼', text: t('empty_state.analyze_documents'), color: '#8b5cf6' },
    { icon: '🔍', text: t('empty_state.review_compliance'), color: '#f59e0b' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSubmit(inputValue);
      setInputValue('');
    }
  };

  const handleUseCaseClick = (text) => {
    onSubmit(text);
  };

  return (
    <div className={styles.emptyState}>
      <h1 className={styles.greeting}>{t('empty_state.title')} ✨</h1>
      <p className={styles.subtext}>
        {t('empty_state.subtitle')}
      </p>
      
      <div className={styles.inputContainer}>
        <form onSubmit={handleSubmit}>
          <div className={styles.inputWrapper}>
            <input
              type="text"
              className={styles.inputField}
              placeholder="Ask me anything"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
            <div className={styles.inputIcons}>
              <button type="button" className={styles.inputButton}>
                <FontAwesomeIcon icon={faPaperclip} />
              </button>
              <button type="button" className={styles.inputButton}>
                <FontAwesomeIcon icon={faGear} /> <span>Tools</span>
              </button>
              <button type="submit" className={styles.submitButton}>
                <FontAwesomeIcon icon={faArrowRight} />
              </button>
            </div>
          </div>
        </form>
      </div>

      <div className={styles.useCasesSection}>
        <p className={styles.useCasesTitle}>{t('empty_state.use_cases')}</p>
        <div className={styles.useCasesGrid}>
          {useCases.map((useCase, index) => (
            <div
              key={index}
              className={styles.useCaseCard}
              onClick={() => handleUseCaseClick(useCase.text)}
            >
              <div className={styles.useCaseIcon} style={{ color: useCase.color }}>
                {useCase.icon}
              </div>
              <p className={styles.useCaseText}>{useCase.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EmptyState;
