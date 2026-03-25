import { createContext, useContext, useState, useCallback } from 'react';
import { translations } from './translations';

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    const saved = localStorage.getItem('starforge-language');
    if (saved) return saved;
    const browserLang = navigator.language.toLowerCase();
    if (browserLang.startsWith('zh')) return 'zh';
    return 'en';
  });

  const changeLanguage = useCallback((lang) => {
    if (translations[lang]) {
      setLanguage(lang);
      localStorage.setItem('starforge-language', lang);
    }
  }, []);

  const toggleLanguage = useCallback(() => {
    changeLanguage(language === 'en' ? 'zh' : 'en');
  }, [language, changeLanguage]);

  const t = useCallback((key) => {
    return translations[language]?.[key] || translations['en']?.[key] || key;
  }, [language]);

  return (
    <LanguageContext.Provider value={{ language, changeLanguage, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
