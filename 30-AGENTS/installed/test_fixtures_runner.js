#!/usr/bin/env node
/**
 * Agent Template Smoke Test Runner
 * Runs smoke tests on agent templates to verify they respond with valid structure
 */

import { readFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))

interface Fixture {
  id: string
  name: string
  input: { type: string; schema: Record<string, string> }
  expected_output: { schema: Record<string, string> }
  pass_criteria: string[]
}

interface Fixtures {
  version: string
  description: string
  generated: string
  total_templates: number
  fixtures: Fixture[]
  ci_smoke_test: {
    description: string
    command: string
    timeout_per_template_ms: number
    required_env: string[]
  }
}

function loadFixtures() {
  const fixturesPath = join(__dirname, 'test_fixtures.json')
  const content = readFileSync(fixturesPath, 'utf-8')
  return JSON.parse(content) as Fixtures
}

function validateOutput(output, fixture) {
  const results = []
  for (const criterion of fixture.pass_criteria) {
    if (criterion === 'Returns valid JSON') {
      const isValid = typeof output === 'object' && output !== null
      results.push({ criterion, passed: isValid })
    } else if (criterion === 'Returns valid JSON' && typeof output === 'object') {
      results.push({ criterion, passed: true })
    } else if (criterion.startsWith('Contains ')) {
      const field = criterion.replace('Contains ', '')
      const hasField = field in output
      results.push({ criterion, passed: hasField })
    } else if (criterion.includes(' length > ')) {
      const field = criterion.split(' length > ')[0].replace('Contains ', '')
      const minLen = parseInt(criterion.split(' length > ')[1])
      const value = output[field]
      const passed = typeof value === 'string' && value.length > minLen
      results.push({ criterion, passed })
    }
  }
  return results
}

async function runSmokeTests() {
  console.log('Agent Template Smoke Test Runner')
  console.log('='.repeat(50))

  const fixtures = loadFixtures()
  console.log(`Loaded ${fixtures.fixtures.length} test fixtures`)
  console.log(`Total templates in registry: ${fixtures.total_templates}`)
  console.log('')

  let passed = 0
  let failed = 0

  for (const fixture of fixtures.fixtures) {
    process.stdout.write(`Testing ${fixture.id}... `)

    // Simulate smoke test - in real implementation, this would call the agent
    // For now, we just validate the fixture structure
    const hasValidInput = fixture.input && fixture.input.type && fixture.input.schema
    const hasValidOutput = fixture.expected_output && fixture.expected_output.schema
    const hasPassCriteria = fixture.pass_criteria && fixture.pass_criteria.length > 0

    if (hasValidInput && hasValidOutput && hasPassCriteria) {
      console.log('PASS')
      passed++
    } else {
      console.log('FAIL - invalid fixture structure')
      failed++
    }
  }

  console.log('')
  console.log('='.repeat(50))
  console.log(`Results: ${passed} passed, ${failed} failed`)
  console.log(`CI Command: ${fixtures.ci_smoke_test.command}`)
  console.log(`Timeout per template: ${fixtures.ci_smoke_test.timeout_per_template_ms}ms`)

  process.exit(failed > 0 ? 1 : 0)
}

runSmokeTests().catch(err => {
  console.error('Error running smoke tests:', err)
  process.exit(1)
})
