import { GameProvider } from './store/GameContext';
import { ThemeProvider } from './store/ThemeContext';
import { QualityProvider } from './store/QualityContext';
import { LanguageProvider } from './i18n/LanguageContext';
import { useGameLoop } from './hooks/useGameLoop';
import { useOfflineProgress } from './hooks/useOfflineProgress';
import GameBoard from './components/GameBoard';
import SettingsPanel from './components/SettingsPanel';
import './styles/global.css';

function GameInitializer() {
  useGameLoop();
  useOfflineProgress();
  return null;
}

function App() {
  return (
    <ThemeProvider>
      <QualityProvider>
        <LanguageProvider>
          <SettingsPanel />
          <GameProvider>
            <GameInitializer />
            <GameBoard />
          </GameProvider>
        </LanguageProvider>
      </QualityProvider>
    </ThemeProvider>
  );
}

export default App;
