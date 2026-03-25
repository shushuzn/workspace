import { GameProvider } from './store/GameContext';
import { QualityProvider } from './store/QualityContext';
import { LanguageProvider } from './i18n/LanguageContext';
import { useGameLoop } from './hooks/useGameLoop';
import { useOfflineProgress } from './hooks/useOfflineProgress';
import GameBoard from './components/GameBoard';
import HotkeyHint from './components/HotkeyHint';
import './styles/global.css';
import './index.css';

function GameInitializer() {
  useGameLoop();
  useOfflineProgress();
  return null;
}

export default function App() {
  return (
    <LanguageProvider>
      <QualityProvider>
        <GameProvider>
          <GameInitializer />
          <GameBoard />
          <HotkeyHint />
        </GameProvider>
      </QualityProvider>
    </LanguageProvider>
  );
}
