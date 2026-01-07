import React from 'react';
// import ThemeToggle from '../ThemeToggle/ThemeToggle';
import styles from './Header.module.scss';

const Header = ({ title, onMenuClick, onNewChat }) => {
  return (
    <header className={styles.header}>
      <div className={styles['header-left']}>
        <button className={styles['menu-icon']} aria-label="Menu" onClick={onMenuClick}>☰</button>
        <h1 className={styles.title}>{title}</h1>
      </div>
      <div className={styles['header-right']}>
        {/* <ThemeToggle /> */}
        <button className={styles['compose-icon']} aria-label="New Chat" onClick={onNewChat}>✏️</button>
      </div>
    </header>
  );
};

export default Header;
