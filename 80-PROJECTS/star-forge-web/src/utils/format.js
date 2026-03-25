// Number formatting utilities

const SUFFIXES = [
  { value: 1e3, suffix: 'K' },
  { value: 1e6, suffix: 'M' },
  { value: 1e9, suffix: 'B' },
  { value: 1e12, suffix: 'T' },
  { value: 1e15, suffix: 'Qa' },
  { value: 1e18, suffix: 'Qi' },
  { value: 1e21, suffix: 'Sx' },
  { value: 1e24, suffix: 'Sp' },
  { value: 1e27, suffix: 'Oc' },
  { value: 1e30, suffix: 'No' },
  { value: 1e33, suffix: 'Dc' },
];

export function formatNumber(num) {
  if (num < 1000) {
    return num < 10 ? num.toFixed(1) : Math.floor(num).toString();
  }

  for (let i = SUFFIXES.length - 1; i >= 0; i--) {
    if (num >= SUFFIXES[i].value) {
      const value = num / SUFFIXES[i].value;
      return value.toFixed(value < 10 ? 2 : 1) + SUFFIXES[i].suffix;
    }
  }

  return num.toExponential(2);
}

export function formatTime(seconds) {
  if (seconds < 60) return `${Math.floor(seconds)}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  return `${Math.floor(seconds / 86400)}d ${Math.floor((seconds % 86400) / 3600)}h`;
}

export function formatPercent(num) {
  return (num * 100).toFixed(1) + '%';
}
