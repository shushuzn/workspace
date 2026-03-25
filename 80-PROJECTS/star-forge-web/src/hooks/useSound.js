// Sound effects hook with Web Audio API
const audioContext = typeof window !== 'undefined' ? new (window.AudioContext || window.webkitAudioContext)() : null;

export function useSound() {
  const playClick = (comboMultiplier = 1) => {
    if (!audioContext) return;
    try {
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      // Base frequency increases with combo
      const baseFreq = 600 + (comboMultiplier - 1) * 100;
      oscillator.frequency.value = baseFreq;
      oscillator.type = 'sine';
      
      const volume = Math.min(0.15, 0.05 + comboMultiplier * 0.02);
      gainNode.gain.setValueAtTime(volume, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.1);
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.1);
    } catch (e) {}
  };

  const playCombo = (comboLevel) => {
    if (!audioContext || comboLevel < 2) return;
    try {
      // Play combo milestone sound
      const frequencies = [523.25, 659.25, 783.99, 1046.50];
      const freqIndex = Math.min(comboLevel - 2, frequencies.length - 1);
      const freq = frequencies[freqIndex];
      
      const osc = audioContext.createOscillator();
      const gain = audioContext.createGain();
      osc.connect(gain);
      gain.connect(audioContext.destination);
      osc.frequency.value = freq;
      osc.type = 'sine';
      gain.gain.setValueAtTime(0.2, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.3);
      osc.start();
      osc.stop(audioContext.currentTime + 0.3);
    } catch (e) {}
  };

  const playMaxCombo = () => {
    if (!audioContext) return;
    try {
      // Epic sound for max combo
      const notes = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99, 1046.50];
      notes.forEach((freq, i) => {
        setTimeout(() => {
          const osc = audioContext.createOscillator();
          const gain = audioContext.createGain();
          osc.connect(gain);
          gain.connect(audioContext.destination);
          osc.frequency.value = freq;
          osc.type = 'triangle';
          gain.gain.setValueAtTime(0.15, audioContext.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.25);
          osc.start();
          osc.stop(audioContext.currentTime + 0.25);
        }, i * 40);
      });
    } catch (e) {}
  };

  const playPurchase = () => {
    if (!audioContext) return;
    try {
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(800, audioContext.currentTime + 0.1);
      oscillator.type = 'triangle';
      gainNode.gain.setValueAtTime(0.15, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.15);
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.15);
    } catch (e) {}
  };

  const playAchievement = () => {
    if (!audioContext) return;
    try {
      const notes = [523.25, 659.25, 783.99];
      notes.forEach((freq, i) => {
        setTimeout(() => {
          const osc = audioContext.createOscillator();
          const gain = audioContext.createGain();
          osc.connect(gain);
          gain.connect(audioContext.destination);
          osc.frequency.value = freq;
          osc.type = 'sine';
          gain.gain.setValueAtTime(0.15, audioContext.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.2);
          osc.start();
          osc.stop(audioContext.currentTime + 0.2);
        }, i * 100);
      });
    } catch (e) {}
  };

  const playPrestige = () => {
    if (!audioContext) return;
    try {
      for (let i = 0; i < 8; i++) {
        setTimeout(() => {
          const osc = audioContext.createOscillator();
          const gain = audioContext.createGain();
          osc.connect(gain);
          gain.connect(audioContext.destination);
          osc.frequency.value = 100 + i * 80;
          osc.type = 'sawtooth';
          gain.gain.setValueAtTime(0.12, audioContext.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.35);
          osc.start();
          osc.stop(audioContext.currentTime + 0.35);
        }, i * 40);
      }
    } catch (e) {}
  };

  return { playClick, playCombo, playMaxCombo, playPurchase, playAchievement, playPrestige };
}
