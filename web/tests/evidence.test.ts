import { test } from 'node:test'
import assert from 'node:assert/strict'
import { selectedOutcome, liveAction } from '../src/evidence.ts'

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

test('a live failure offers a bounded retry and never acceptance', () => {
  assert.equal(liveAction('INCONCLUSIVE', 1, 'coupon-01').command, '@synkai-verifier retry coupon-01')
  assert.equal(liveAction('INCONCLUSIVE', 2, 'coupon-01').command, null)
  assert.equal(liveAction('VERIFYING', 1, 'coupon-01').command, null)
})

test('human decisions are explicit at the beginning and end', () => {
  assert.equal(liveAction('NEEDS_APPROVAL', 0, 'coupon-01').command, '@synkai-verifier approve coupon-01')
  assert.equal(liveAction('AWAITING_REVIEW', 1, 'coupon-01').command, '@synkai-verifier accept coupon-01')
  assert.equal(liveAction('CLOSED', 1, 'coupon-01').command, null)
})
