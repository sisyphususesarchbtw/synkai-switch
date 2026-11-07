export function selectedOutcome(currentCandidate: string | null | undefined, selectedCandidate: string | undefined, outcome: string): string {
  return currentCandidate && selectedCandidate && currentCandidate === selectedCandidate ? outcome : 'NOT_RUN'
}

export function liveAction(status: string, attempts: number, id: string): { title: string; detail: string; command: string | null } {
  const prefix = '@synkai-verifier '
  if (status === 'NEEDS_APPROVAL') return { title: 'Your decision comes first.', detail: 'Review the proposed behavior, then approve it in the source room.', command: prefix + 'approve ' + id }
  if (status === 'AWAITING_REVIEW') return { title: 'The evidence is ready.', detail: 'Inspect the patch and recorded checks. Accept it in the source room when satisfied.', command: prefix + 'accept ' + id }
  if (status === 'CLOSED') return { title: 'Accepted by the operator.', detail: 'The patch, original approval and execution record remain available below.', command: null }
  if (status === 'STALE') return { title: 'Evidence invalidated.', detail: 'Inputs or candidate revision changed. A new verification run is required before acceptance.', command: null }
  if (status === 'INCONCLUSIVE' || status === 'REJECTED') return { title: 'The workflow stopped.', detail: attempts < 2 ? 'Inspect the failure. One coding attempt remains; a retry needs your instruction.' : 'The two-attempt budget is exhausted. No further coding call will run automatically.', command: status === 'INCONCLUSIVE' && attempts === 1 ? prefix + 'retry ' + id : null }
  return { title: status === 'VERIFYING' ? 'Checking the proposed repair.' : 'The agents are working.', detail: 'The result appears after execution. Agent connection status is shown separately.', command: null }
}
