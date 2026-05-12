export function compactSafetyNumber(safetyNumber: string): string {
  return safetyNumber.replace(/\s/g, "");
}

export function formatSafetyNumberPreview(safetyNumber: string): string {
  const compact = compactSafetyNumber(safetyNumber);
  return `${compact.slice(0, 10)} ${compact.slice(-10)}`;
}

export function safetyNumberMatches(expected: string, presented: string): boolean {
  return compactSafetyNumber(expected) === compactSafetyNumber(presented);
}
