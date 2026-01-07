import React from 'react';
// import ThemeToggle from '../ThemeToggle/ThemeToggle';
import styles from './Header.module.scss';

const Header = ({ title, onMenuClick, onNewChat }) => {
  return (
    <header className={styles.header}>
      <div className={styles.headerLeft}>
        <button className={styles.menuIcon} aria-label="Menu" onClick={onMenuClick}>☰</button>
        <h1 className={styles.title}>{title}</h1>
      </div>
      <div className={styles.headerRight}>
        {/* <ThemeToggle /> */}
        <button className={styles.composeIcon} aria-label="New Chat" onClick={onNewChat}>✏️</button>
      </div>
    </header>
  );
};

export default Header;
