# Unified Data Export API

60-DATA collector统一导出接口，支持CSV/JSON/Parquet格式。

## Usage

```bash
# List all available collectors
node exporter.js list

# Export health_001 as JSON
node exporter.js export health_001 json

# Export health_001 as CSV
node exporter.js export health_001 csv

# Get schema for a collector
node exporter.js schema health_001
```

## Supported Collectors

| Collector | Description | Formats |
|-----------|-------------|---------|
| health_001 | System health and tool registry status | JSON, CSV |
| advisor_001 | AI advisor suggestions and history | JSON, CSV |
| audit_001 | Audit log entries | JSON, CSV |
| batch_001 | Batch processing jobs | JSON, CSV |

## Export Schema

Each collector exports with documented fields. See `exporter.js` for the full schema definition.
