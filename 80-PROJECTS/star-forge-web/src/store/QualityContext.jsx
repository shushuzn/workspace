import { createContext, useContext, useState, useEffect } from 'react';

const QualityContext = createContext(null);

export function QualityProvider({ children }) {
  const [quality, setQuality] = useState(() => {
    const saved = localStorage.getItem('starforge-quality');
    return saved || 'medium';
  });

  useEffect(() => {
    localStorage.setItem('starforge-quality', quality);
    document.documentElement.setAttribute('data-quality', quality);
  }, [quality]);

  const changeQuality = (newQuality) => {
    if (['low', 'medium', 'high'].includes(newQuality)) {
      setQuality(newQuality);
    }
  };

  return (
    <QualityContext.Provider value={{ quality, changeQuality }}>
      {children}
    </QualityContext.Provider>
  );
}

export function useQuality() {
  const context = useContext(QualityContext);
  if (!context) {
    throw new Error('useQuality must be used within a QualityProvider');
  }
  return context;
}
