# Crucix i18n Module

## Usage

```js
import { t, getLocale, getLanguage, getSupportedLocales } from './i18n.mjs';

// Get current language
const lang = getLanguage(); // 'en', 'fr', or 'zh'

// Translate a key
t('dashboard.title') // 'CRUCIX — Intelligence Terminal'
t('dashboard.sweep', { count: 25 }) // 'Sweep — 25 sources'

// Get full locale object
const locale = getLocale();

// Add locale files
// locales/en.json, locales/fr.json, locales/zh.json
```

## Environment Variables

- `I18N_LANG` — Override language (takes priority)
- `LANGUAGE` — Linux/macOS system language
- `LANG` — Fallback locale

## Locale File Format

```json
{
  "meta": { "code": "en", "name": "English", "nativeName": "English" },
  "dashboard": { "title": "My App", "sweep": "Sweep — {count} sources" },
  "errors": { "notFound": "Not found" }
}
```
