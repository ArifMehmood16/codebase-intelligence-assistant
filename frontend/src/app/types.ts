export type IngestStatus = "completed" | "failed" | "pending" | "indexing" | string;

/** Repository summary mapped from the ingest/list API. */
export type Repository = {
  repositoryId: string;
  status: IngestStatus;
  indexedFileCount: number;
  ignoredFileCount: number;
  indexedPaths: string[];
  ignoredReasonCounts: { reason: string; count: number }[];
  failureCode: string | null;
  sourceFilename: string | null;
  card: RepositoryCardView | null;
};

/** @deprecated Prefer Repository — kept for gradual rename in tests. */
export type IngestSummary = Repository;

export type ExtractedEndpointView = {
  method: string;
  path: string;
  filePath: string;
  startLine: number;
  endLine: number;
};

export type DeclaredDependencyView = {
  name: string;
  filePath: string;
  startLine: number;
  endLine: number;
};

export type RepositoryCardView = {
  displayName: string;
  readmePath: string | null;
  readmeExcerpt: string;
  manifestName: string | null;
  manifestDescription: string | null;
  dependencies: string[];
  languages: { language: string; count: number }[];
  outlinePaths: string[];
  outlineTruncated: boolean;
  declaredDependencies: DeclaredDependencyView[];
  endpoints: ExtractedEndpointView[];
};

export type Citation = {
  filePath: string;
  startLine: number;
  endLine: number;
  excerpt: string;
};

/** @deprecated Prefer Citation */
export type CitationView = Citation;

export type AnswerView = {
  text: string;
  insufficientEvidence: boolean;
  citations: Citation[];
};

export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: number;
  citations?: Citation[];
  insufficientEvidence?: boolean;
  error?: string;
  pending?: boolean;
  statusLine?: string;
};

export type RepositoryListResponse = {
  repositories: RepositoryApiItem[];
};

export type RepositoryCardApi = {
  display_name: string;
  readme_path: string | null;
  readme_excerpt: string;
  manifest_name: string | null;
  manifest_description: string | null;
  dependencies: string[];
  languages: { language: string; count: number }[];
  outline_paths: string[];
  outline_truncated: boolean;
  declared_dependencies?: {
    name: string;
    file_path: string;
    start_line: number;
    end_line: number;
  }[];
  endpoints?: {
    method: string;
    path: string;
    file_path: string;
    start_line: number;
    end_line: number;
  }[];
};

export type RepositoryApiItem = {
  repository_id: string;
  status?: string;
  indexed_file_count: number;
  ignored_file_count: number;
  indexed_paths: string[];
  ignored_reason_counts: { reason: string; count: number }[];
  failure_code?: string | null;
  source_filename?: string | null;
  repository_card?: RepositoryCardApi | null;
};

export type AskResponseApi = {
  text: string;
  insufficient_evidence: boolean;
  citations: {
    file_path: string;
    start_line: number;
    end_line: number;
    excerpt: string;
  }[];
};

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

export function mapIngestSummary(body: RepositoryApiItem): Repository {
  return {
    repositoryId: body.repository_id,
    status: body.status ?? "completed",
    indexedFileCount: body.indexed_file_count,
    ignoredFileCount: body.ignored_file_count,
    indexedPaths: body.indexed_paths,
    ignoredReasonCounts: body.ignored_reason_counts,
    failureCode: body.failure_code ?? null,
    sourceFilename: body.source_filename ?? null,
    card: mapRepositoryCard(body.repository_card),
  };
}

function mapRepositoryCard(
  payload: RepositoryCardApi | null | undefined,
): RepositoryCardView | null {
  if (!payload) {
    return null;
  }
  return {
    displayName: payload.display_name,
    readmePath: payload.readme_path,
    readmeExcerpt: payload.readme_excerpt,
    manifestName: payload.manifest_name,
    manifestDescription: payload.manifest_description,
    dependencies: payload.dependencies,
    languages: payload.languages,
    outlinePaths: payload.outline_paths,
    outlineTruncated: payload.outline_truncated,
    declaredDependencies: (payload.declared_dependencies ?? []).map((item) => ({
      name: item.name,
      filePath: item.file_path,
      startLine: item.start_line,
      endLine: item.end_line,
    })),
    endpoints: (payload.endpoints ?? []).map((item) => ({
      method: item.method,
      path: item.path,
      filePath: item.file_path,
      startLine: item.start_line,
      endLine: item.end_line,
    })),
  };
}

export function stripZipSuffix(name: string): string {
  return name.replace(/\.zip$/i, "");
}

export function repositoryDisplayName(repo: Repository): string {
  if (repo.sourceFilename?.trim()) {
    return stripZipSuffix(repo.sourceFilename.trim());
  }
  const roots = repo.indexedPaths
    .map((path) => path.split("/")[0]?.trim() ?? "")
    .filter((part) => part.length > 0);
  if (roots.length > 0 && roots.every((part) => part === roots[0])) {
    return roots[0];
  }
  return "Untitled repository";
}

/** Case-folded display name used as the unique repository reference. */
export function repositoryNameKey(repo: Repository | string): string | null {
  const raw =
    typeof repo === "string"
      ? repo
      : repo.sourceFilename?.trim() || repositoryDisplayName(repo);
  const name = stripZipSuffix(raw.trim());
  return name ? name.toLowerCase() : null;
}

export function shortHash(id: string): string {
  return id.length > 8 ? id.slice(0, 8) : id;
}

export function truncatePathLeft(path: string, max = 42): string {
  if (path.length <= max) {
    return path;
  }
  return `…${path.slice(-(max - 1))}`;
}

export function relativeTime(fromMs: number, nowMs = Date.now()): string {
  const deltaSec = Math.max(0, Math.round((nowMs - fromMs) / 1000));
  if (deltaSec < 60) {
    return "just now";
  }
  const minutes = Math.round(deltaSec / 60);
  if (minutes < 60) {
    return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  }
  const hours = Math.round(minutes / 60);
  if (hours < 48) {
    return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  }
  const days = Math.round(hours / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}
