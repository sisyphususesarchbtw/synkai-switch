import { test } from 'node:test'
import assert from 'node:assert/strict'
import { selectedOutcome } from '../src/evidence.ts'

test('switching candidates cannot inherit the previous verified result', () => {
  assert.equal(selectedOutcome('repair', 'test-only', 'VERIFIED'), 'NOT_RUN')
})

test('matching candidates retain stale and inconclusive states', () => {
  assert.equal(selectedOutcome('repair', 'repair', 'STALE'), 'STALE')
  assert.equal(selectedOutcome('repair', 'repair', 'INCONCLUSIVE'), 'INCONCLUSIVE')
})

test('a case without a selected revision has no result', () => {
  assert.equal(selectedOutcome(null, undefined, 'VERIFIED'), 'NOT_RUN')
})
