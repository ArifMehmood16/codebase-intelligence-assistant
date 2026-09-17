import { loadFrontendConfig } from "./config";
import type { AnswerView, AskResponseApi, Repository, RepositoryApiItem } from "./types";
import { ApiError, mapIngestSummary } from "./types";

export type FetchOptions = {
  fetcher?: typeof fetch;
  signal?: AbortSignal;
};

export async function listRepositories(
  options: FetchOptions = {},
): Promise<Repository[]> {
  const fetcher = options.fetcher ?? fetch;
  const { apiBaseUrl } = loadFrontendConfig();
  const response = await fetcher(`${apiBaseUrl}/api/repositories`, {
    signal: options.signal,
  });
  if (!response.ok) {
    throw new ApiError(response.status, await safeMessage(response));
  }
  const body = (await response.json()) as {
    repositories: RepositoryApiItem[];
  };
  return body.repositories.map(mapIngestSummary);
}

export async function getRepository(
  repositoryId: string,
  options: FetchOptions = {},
): Promise<Repository> {
  const fetcher = options.fetcher ?? fetch;
  const { apiBaseUrl } = loadFrontendConfig();
  const response = await fetcher(
    `${apiBaseUrl}/api/repositories/${encodeURIComponent(repositoryId)}`,
    { signal: options.signal },
  );
  if (!response.ok) {
    throw new ApiError(response.status, await safeMessage(response));
  }
  return mapIngestSummary((await response.json()) as RepositoryApiItem);
}

export async function ingestZip(
  file: File,
  options: FetchOptions = {},
): Promise<Repository> {
  const fetcher = options.fetcher ?? fetch;
  const { apiBaseUrl } = loadFrontendConfig();
  const filename = encodeURIComponent(file.name);
  const response = await fetcher(
    `${apiBaseUrl}/api/repositories?filename=${filename}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/zip" },
      body: file,
      signal: options.signal,
    },
  );
  if (!response.ok) {
    throw new ApiError(response.status, await safeMessage(response));
  }
  return mapIngestSummary((await response.json()) as RepositoryApiItem);
}

export async function deleteRepository(
  repositoryId: string,
  options: FetchOptions = {},
): Promise<void> {
  const fetcher = options.fetcher ?? fetch;
  const { apiBaseUrl } = loadFrontendConfig();
  const response = await fetcher(
    `${apiBaseUrl}/api/repositories/${encodeURIComponent(repositoryId)}`,
    {
      method: "DELETE",
      signal: options.signal,
    },
  );
  if (!response.ok) {
    throw new ApiError(response.status, await safeMessage(response));
  }
}

export async function askQuestion(
  repositoryId: string,
  question: string,
  options: FetchOptions = {},
): Promise<AnswerView> {
  const fetcher = options.fetcher ?? fetch;
  const { apiBaseUrl } = loadFrontendConfig();
  const response = await fetcher(
    `${apiBaseUrl}/api/repositories/${encodeURIComponent(repositoryId)}/questions`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
      signal: options.signal,
    },
  );
  if (!response.ok) {
    throw new ApiError(response.status, await safeMessage(response));
  }
  const body = (await response.json()) as AskResponseApi;
  return {
    text: body.text,
    insufficientEvidence: body.insufficient_evidence,
    citations: body.citations.map((citation) => ({
      filePath: citation.file_path,
      startLine: citation.start_line,
      endLine: citation.end_line,
      excerpt: citation.excerpt,
    })),
  };
}

async function safeMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") {
      return body.detail;
    }
  } catch {
    /* use status text */
  }
  return response.statusText || "Request failed";
}
