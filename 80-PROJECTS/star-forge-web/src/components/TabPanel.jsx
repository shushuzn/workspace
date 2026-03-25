import { useState } from 'react';
import BuildingPanel from './BuildingPanel';
import UpgradePanel from './UpgradePanel';
import PrestigePanel from './PrestigePanel';
import StatsPanel from './StatsPanel';
import { useLanguage } from '../i18n/LanguageContext';
import styles from './TabPanel.module.css';

export default function TabPanel({ showStats }) {
  const [activeTab, setActiveTab] = useState('buildings');
  const { t } = useLanguage();

  if (showStats) {
    return <StatsPanel />;
  }

  const tabs = [
    { id: 'buildings', label: t('building.title'), icon: '🏗️' },
    { id: 'upgrades', label: t('upgrade.title'), icon: '⬆️' },
    { id: 'prestige', label: t('prestige.title'), icon: '✨' },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'buildings':
        return <BuildingPanel />;
      case 'upgrades':
        return <UpgradePanel />;
      case 'prestige':
        return <PrestigePanel />;
      default:
        return null;
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.tabBar}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`${styles.tab} ${activeTab === tab.id ? styles.active : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className={styles.icon}>{tab.icon}</span>
            <span className={styles.label}>{tab.label}</span>
          </button>
        ))}
      </div>
      <div className={styles.content}>
        {renderContent()}
      </div>
    </div>
  );
}
