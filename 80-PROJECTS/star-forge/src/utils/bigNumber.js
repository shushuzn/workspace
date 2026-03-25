// Big number handling to avoid JavaScript floating point issues

const THRESHOLD = 1e15; // Beyond this, use big number arithmetic

export function toBigNumber(num) {
  if (num >= THRESHOLD) {
    return {
      value: num,
      isBig: true
    };
  }
  return { value: Math.floor(num), isBig: false };
}

export function add(a, b) {
  return Math.floor(a + b);
}

export function subtract(a, b) {
  return Math.max(0, Math.floor(a - b));
}

export function multiply(a, b) {
  return Math.floor(a * b);
}

export function divide(a, b) {
  if (b === 0) return 0;
  return Math.floor(a / b);
}

export function sqrt(num) {
  return Math.floor(Math.sqrt(num));
}

export function pow(base, exp) {
  return Math.pow(base, exp);
}

export function min(a, b) {
  return Math.min(a, b);
}

export function max(a, b) {
  return Math.max(a, b);
}
