import { describe, it, expect } from 'vitest';
import { formatNumber, formatTime, formatPercent } from '../src/utils/format.js';

describe('format utilities', () => {
  describe('formatNumber', () => {
    it('should format small numbers without abbreviation', () => {
      expect(formatNumber(100)).toBe('100');
      expect(formatNumber(999)).toBe('999');
    });

    it('should format thousands with K abbreviation', () => {
      expect(formatNumber(1000)).toContain('K');
      expect(formatNumber(10000)).toContain('K');
    });

    it('should format millions with M abbreviation', () => {
      expect(formatNumber(1000000)).toContain('M');
    });

    it('should format billions with B abbreviation', () => {
      expect(formatNumber(1000000000)).toContain('B');
    });

    it('should handle zero', () => {
      expect(formatNumber(0)).toBe('0.0');
    });

    it('should handle negative numbers', () => {
      expect(formatNumber(-1000)).toContain('-');
    });
  });

  describe('formatTime', () => {
    it('should format seconds correctly', () => {
      expect(formatTime(30)).toBe('30s');
    });

    it('should format minutes correctly', () => {
      expect(formatTime(60)).toBe('1m 0s');
      expect(formatTime(90)).toBe('1m 30s');
    });

    it('should format hours correctly', () => {
      expect(formatTime(3600)).toContain('h');
    });

    it('should format days correctly', () => {
      expect(formatTime(86400)).toContain('d');
    });
  });

  describe('formatPercent', () => {
    it('should format percentage correctly', () => {
      expect(formatPercent(0.5)).toBe('50.0%');
      expect(formatPercent(1.0)).toBe('100.0%');
    });

    it('should handle decimal values', () => {
      const result = formatPercent(0.3333);
      expect(result).toContain('%');
    });

    it('should handle zero', () => {
      expect(formatPercent(0)).toBe('0.0%');
    });
  });
});
