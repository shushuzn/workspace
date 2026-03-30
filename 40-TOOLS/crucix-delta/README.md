# Crucix Delta Engine Module

## Usage

```js
import { computeDelta, MemoryManager } from './index.mjs';

// Compute changes between two snapshots
const current = { fred: [{id:'VIXCLS', value:30}], energy: {wti:75}, ... };
const previous = { fred: [{id:'VIXCLS', value:25}], energy: {wti:70}, ... };

const delta = computeDelta(current, previous);
console.log(delta.summary.direction);  // 'risk-off', 'risk-on', or 'mixed'
console.log(delta.signals.escalated); // array of changed signals
console.log(delta.summary.criticalChanges);
```

## MemoryManager

```js
const memory = new MemoryManager('./runs');

// Add a run and get delta
const delta = memory.addRun(synthesizedData);

// Check alert suppression
if (!memory.isSignalSuppressed('vix_spike')) {
  memory.markAsAlerted('vix_spike', new Date().toISOString());
}
```

## Delta Thresholds

Numeric thresholds (percentage change):
- VIX: ±5%
- WTI/Brent: ±3%
- Gold: ±2%

Count thresholds (absolute change):
- Urgent posts: ±2
- Thermal detections: ±500
- Conflict events: ±5
