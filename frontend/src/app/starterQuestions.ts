import type { Repository } from "./types";

const OVERVIEW = "What does this repo do?";
const STRUCTURE = "What is the directory structure?";
const ENDPOINTS = "What API endpoints exist?";
const DEPENDENCIES = "What dependencies does this project declare?";
const LIST_ITEMS = "Where is list_items defined?";
const MAX_CHIPS = 4;
const CODE_SUFFIX = /\.(py|ts|tsx|js|jsx|java|go|rb|cs|kt|php)$/i;

export function starterQuestions(repository: Repository): string[] {
  const files = indexedFiles(repository);
  const chips: string[] = [OVERVIEW, STRUCTURE];
  if (files.some(isHandlersPath)) {
    chips.push(LIST_ITEMS);
  }
  if ((repository.card?.endpoints.length ?? 0) > 0) {
    chips.push(ENDPOINTS);
  }
  if (
    (repository.card?.dependencies.length ?? 0) > 0 ||
    (repository.card?.declaredDependencies.length ?? 0) > 0
  ) {
    chips.push(DEPENDENCIES);
  }
  if (chips.length < MAX_CHIPS) {
    const locate = locateQuestion(files);
    if (locate && !chips.includes(locate)) {
      chips.push(locate);
    }
  }
  return chips.slice(0, MAX_CHIPS);
}

function indexedFiles(repository: Repository): string[] {
  const fromIndex = repository.indexedPaths.filter(isFilePath);
  if (fromIndex.length > 0) {
    return fromIndex;
  }
  return (repository.card?.outlinePaths ?? []).filter(isFilePath);
}

function isFilePath(path: string): boolean {
  return Boolean(path) && !path.endsWith("/");
}

function isHandlersPath(path: string): boolean {
  return path === "src/api/handlers.py" || path.endsWith("/handlers.py");
}

function locateQuestion(files: string[]): string | null {
  const code = files.find((path) => CODE_SUFFIX.test(path));
  const chosen = code ?? files[0];
  if (!chosen) {
    return null;
  }
  return `Where is ${chosen} implemented?`;
}
