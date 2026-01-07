import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './InputBar.module.scss';

const InputBar = ({ onSendMessage, disabled }) => {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !disabled) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  return (
    <div className={styles['input-container']}>
      <form onSubmit={handleSubmit}>
        <div className={styles['input-wrapper']}>
          <button type="button" className={styles['agents-toggle']}>
            <div className={styles['agent-avatars']}>
              <div className={`${styles['agent-avatar-small']} ${styles.legal}`}>
                <img 
                  src="https://sspark.genspark.ai/cfimages?u1=qRqawqrDk00RQMP6wXEUHuxWslNIbEJeCgy3Kqs9GXjw0sIL8483WOde5qmLhtDY%2Fhw0V%2BGoiSSXpfCp3EeKCA2VGgjvltWHVtZrtmfw3iMJN6A6k3wj&u2=tJ5MdbAFRhq2FK3f&width=2560" 
                  alt={t('app.logo_alt')}
                  className={styles['agent-logo']}
                />
              </div>
            </div>
            <span className={styles['active-text']}>{t('input.legal_assistant')}</span>
          </button>

          <input
            type="text"
            className={styles['input-field']}
            placeholder={t('input.placeholder')}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={disabled}
          />

          <button type="submit" className={styles['icon-button']} disabled={disabled}>
            {disabled ? '⏳' : '➕'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default InputBar;
