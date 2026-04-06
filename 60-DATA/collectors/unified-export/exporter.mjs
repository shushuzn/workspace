/**
 * Unified Data Export API
 * Provides standardized export interface for all 60-DATA collectors
 */

import { readFileSync, readdirSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const DATA_ROOT = join(__dirname, '..', '..')

/**
 * @typedef {'csv' | 'json' | 'parquet'} ExportFormat
 */

/**
 * @typedef {Object} ExportOptions
 * @property {ExportFormat} format - Output format
 * @property {string[]} [fields] - Fields to include (default: all)
 * @property {string} [filter] - Filter expression
 */

/**
 * @typedef {Object} ExportSchema
 * @property {string} name - Collector name
 * @property {ExportFormat[]} supported_formats - Available export formats
 * @property {Object} fields - Field definitions
 * @property {string} description - What this collector does
 */

// Known collectors with their data files
const COLLECTOR_MANIFEST = {
  health_001: {
    name: 'health_001',
    description: 'System health and tool registry status',
    data_file: 'health_report.json',
    fields: {
      timestamp: 'string - Report generation time',
      'tools.total': 'number - Total tools tracked',
      'tools.exists': 'number - Tools with files present',
      'tools.missing': 'number - Missing tool files',
      'registry.total_tools': 'number - Total in registry',
      'registry.active': 'number - Active agents',
      'registry.inactive': 'number - Inactive agents'
    },
    supported_formats: ['json', 'csv']
  },
  advisor_001: {
    name: 'advisor_001',
    description: 'AI advisor suggestions and history',
    data_file: 'advisor_history.json',
    fields: {
      timestamp: 'string - Event timestamp',
      progress_pct: 'number - Progress percentage 0-100',
      next_tool: 'string|null - Next recommended tool'
    },
    supported_formats: ['json', 'csv']
  },
  audit_001: {
    name: 'audit_001',
    description: 'Audit log entries',
    data_file: null,
    fields: {
      timestamp: 'string - Event timestamp',
      action: 'string - Action performed',
      user: 'string - User identifier'
    },
    supported_formats: ['json', 'csv']
  },
  batch_001: {
    name: 'batch_001',
    description: 'Batch processing jobs',
    data_file: null,
    fields: {
      job_id: 'string - Unique job identifier',
      status: 'string - Job status',
      created_at: 'string - Creation timestamp'
    },
    supported_formats: ['json', 'csv']
  }
}

/**
 * Load data from a collector
 * @param {string} collectorId
 * @returns {Object|null}
 */
function loadCollectorData(collectorId) {
  const manifest = COLLECTOR_MANIFEST[collectorId]
  if (!manifest || !manifest.data_file) {
    // Return empty for collectors without static data files
    return []
  }

  const dataPath = join(DATA_ROOT, collectorId, manifest.data_file)
  try {
    const content = readFileSync(dataPath, 'utf-8')
    return JSON.parse(content)
  } catch (err) {
    console.warn(`Warning: Could not load data for ${collectorId}:`, err.message)
    return null
  }
}

/**
 * Convert data to CSV format
 * @param {Object|Object[]} data
 * @param {string[]} [fields]
 * @returns {string}
 */
function toCSV(data, fields) {
  const items = Array.isArray(data) ? data : [data]
  if (items.length === 0) return ''

  const allKeys = fields || Object.keys(items[0] || {})

  const header = allKeys.join(',')
  const rows = items.map(item =>
    allKeys.map(key => {
      const value = key.split('.').reduce((obj, k) => obj?.[k], item)
      const str = value === null || value === undefined ? '' : String(value)
      return str.includes(',') || str.includes('"') || str.includes('\n')
        ? `"${str.replace(/"/g, '""')}"`
        : str
    }).join(',')
  )

  return [header, ...rows].join('\n')
}

/**
 * Export data from a collector
 * @param {string} collectorId
 * @param {ExportOptions} options
 * @returns {string}
 */
function exportCollector(collectorId, options = {}) {
  const format = options.format || 'json'
  const data = loadCollectorData(collectorId)

  if (data === null) {
    return JSON.stringify({ error: `No data available for ${collectorId}` })
  }

  switch (format) {
    case 'csv':
      return toCSV(data, options.fields)
    case 'json':
    default:
      return JSON.stringify(data, null, 2)
  }
}

/**
 * List all available collectors
 * @returns {ExportSchema[]}
 */
function listCollectors() {
  return Object.values(COLLECTOR_MANIFEST).map(m => ({
    name: m.name,
    description: m.description,
    supported_formats: m.supported_formats,
    fields: m.fields
  }))
}

/**
 * Get export schema for a specific collector
 * @param {string} collectorId
 * @returns {ExportSchema|null}
 */
function getExportSchema(collectorId) {
  return COLLECTOR_MANIFEST[collectorId] || null
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2)
  const command = args[0]

  if (command === 'list') {
    console.log(JSON.stringify(listCollectors(), null, 2))
  } else if (command === 'export') {
    const collectorId = args[1]
    const format = (args[2] || 'json').replace('--format=', '')
    if (!collectorId) {
      console.error('Usage: exporter.js export <collector_id> [csv|json]')
      process.exit(1)
    }
    console.log(exportCollector(collectorId, { format }))
  } else if (command === 'schema') {
    const collectorId = args[1]
    if (!collectorId) {
      console.error('Usage: exporter.js schema <collector_id>')
      process.exit(1)
    }
    console.log(JSON.stringify(getExportSchema(collectorId), null, 2))
  } else {
    console.log('Unified Data Export API')
    console.log('Usage:')
    console.log('  exporter.js list                    - List all collectors')
    console.log('  exporter.js export <id> [csv|json]  - Export collector data')
    console.log('  exporter.js schema <id>             - Get export schema')
  }
}

export { exportCollector, listCollectors, getExportSchema, COLLECTOR_MANIFEST }
