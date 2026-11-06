export function selectedOutcome(currentCandidate: string | null | undefined, selectedCandidate: string | undefined, outcome: string): string {
  return currentCandidate && selectedCandidate && currentCandidate === selectedCandidate ? outcome : 'NOT_RUN'
}
