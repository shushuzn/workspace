// shared/temperatureScheduler.js

export class TemperatureScheduler {
  constructor(config = {}) {
    this.config = {
      initialTemp: config.initialTemp ?? 1.2,
      coolingRate: config.coolingRate ?? 0.88,
      minTemp: config.minTemp ?? 0.3,
      plateauRounds: config.plateauRounds ?? 2,
      earlyStopDeltaS: config.earlyStopDeltaS ?? 0.05,
      deltaSThreshold: config.deltaSThreshold ?? 0.35,
      minRoundsBeforeEarlyStop: config.minRoundsBeforeEarlyStop ?? 4,
      ...config,
    };
    this.currentTemp = this.config.initialTemp;
    this.deltaSHistory = [];
    this.roundsSinceSignificantDelta = 0;
    this.criticalDetected = false;
    this.plateauRemaining = 0;
    this.plateauTemperature = null;
    this.tempHistory = [];
  }

  /** 获取当前轮温度（不在此处 push tempHistory，由调用方管理） */
  getTemperature() {
    if (this.plateauRemaining > 0) {
      return Math.max(this.plateauTemperature ?? this.currentTemp, this.config.minTemp);
    }
    return Math.max(this.currentTemp, this.config.minTemp);
  }

  /** 记录本轮温度（由主循环调用，每轮只 push 一次） */
  pushTempHistory(t) {
    this.tempHistory.push(t);
  }

  /** 记录本轮 ΔS */
  recordDeltaS(deltaS) {
    this.deltaSHistory.push(deltaS);
    if (deltaS < this.config.earlyStopDeltaS) {
      this.roundsSinceSignificantDelta++;
    } else {
      this.roundsSinceSignificantDelta = 0;
    }
  }

  /** 检测是否应进入 plateau */
  shouldEnterPlateau() {
    if (this.deltaSHistory.length < 3) return false;
    if (this.criticalDetected) return false;
    const n = this.deltaSHistory.length;
    const prev = this.deltaSHistory[n - 2];
    const curr = this.deltaSHistory[n - 1];
    return curr > prev && curr > this.config.deltaSThreshold;
  }

  /** 进入 plateau */
  enterPlateau() {
    this.criticalDetected = true;
    this.plateauRemaining = this.config.plateauRounds;
    this.plateauTemperature = this.currentTemp;
  }

  /** 进入下一轮 */
  nextRound() {
    if (this.plateauRemaining > 0) {
      this.plateauRemaining--;
      if (this.plateauRemaining === 0) {
        this.currentTemp = this.plateauTemperature ?? this.currentTemp;
      }
    } else {
      this.currentTemp *= this.config.coolingRate;
    }
  }

  /** 连续几轮无显著 ΔS */
  getRoundsSinceLastSignificantDelta() {
    return this.roundsSinceSignificantDelta;
  }

  /** 获取所有统计信息（供报告使用） */
  getStats() {
    return {
      tempHistory: this.tempHistory,
      deltaSHistory: this.deltaSHistory,
      criticalTemp: this.plateauTemperature,
      criticalDetected: this.criticalDetected,
    };
  }
}
