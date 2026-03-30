// Internationalization (i18n) Module
// Loads locale files and provides translation functions

import { readFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const LOCALES_DIR = join(__dirname, '..', 'locales');

const SUPPORTED_LOCALES = ['en', 'fr', 'zh'];
const DEFAULT_LOCALE = 'en';
const localeCache = new Map();

export function getLanguage() {
  const lang = (process.env.I18N_LANG || process.env.LANGUAGE || process.env.LANG || DEFAULT_LOCALE)
    .toLowerCase().slice(0, 2);
  return SUPPORTED_LOCALES.includes(lang) ? lang : DEFAULT_LOCALE;
}

function loadLocale(lang) {
  if (localeCache.has(lang)) return localeCache.get(lang);
  const localePath = join(LOCALES_DIR, `${lang}.json`);
  if (!existsSync(localePath)) {
    console.warn(`[i18n] Locale not found: ${localePath}`);
    return loadLocale(DEFAULT_LOCALE);
  }
  try {
    const data = JSON.parse(readFileSync(localePath, 'utf-8'));
    localeCache.set(lang, data);
    return data;
  } catch (err) {
    console.error(`[i18n] Load failed: ${err.message}`);
    if (lang !== DEFAULT_LOCALE) return loadLocale(DEFAULT_LOCALE);
    return {};
  }
}

export function getLocale() { return loadLocale(getLanguage()); }

export function t(keyPath, params = {}) {
  const locale = getLocale();
  const keys = keyPath.split('.');
  let value = locale;
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) value = value[key];
    else { console.warn(`[i18n] Missing: ${keyPath}`); return keyPath; }
  }
  if (typeof value !== 'string') return keyPath;
  return value.replace(/\{(\w+)\}/g, (_, key) => params[key] !== undefined ? params[key] : `{${key}}`);
}

export function getSupportedLocales() {
  return SUPPORTED_LOCALES.map(code => {
    const locale = loadLocale(code);
    return { code, name: locale.meta?.name || code, nativeName: locale.meta?.nativeName || code };
  });
}

export function isSupported(lang) { return SUPPORTED_LOCALES.includes(lang?.toLowerCase()?.slice(0, 2)); }

export const currentLanguage = getLanguage();
