import { useState } from 'react';
import styles from './ThemeToggle.module.css';

export default function ThemeToggle({ collapsed = false }) {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  };

  return (
    <button 
      className={`${styles.toggle} ${collapsed ? styles.collapsed : ''}`}
      onClick={toggleTheme}
      title={theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
    >
      <span className={styles.icon}>
        {theme === 'dark' ? '☀️' : '🌙'}
      </span>
      {!collapsed && <span className={styles.label}>{theme === 'dark' ? '浅色' : '深色'}</span>}
    </button>
  );
}
