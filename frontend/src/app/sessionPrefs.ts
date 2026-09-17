const SEEN_KEY = "cia.repoSeenAt.v1";

function readMap(key: string): Record<string, number> {
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) {
      return {};
    }
    const parsed = JSON.parse(raw) as Record<string, number>;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function writeMap(key: string, value: Record<string, number>): void {
  try {
    sessionStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* ignore */
  }
}

export function rememberRepoSeen(repositoryId: string, at = Date.now()): number {
  const map = readMap(SEEN_KEY);
  if (map[repositoryId] == null) {
    map[repositoryId] = at;
    writeMap(SEEN_KEY, map);
  }
  return map[repositoryId];
}

export function getRepoSeenAt(repositoryId: string): number | null {
  const map = readMap(SEEN_KEY);
  return map[repositoryId] ?? null;
}
