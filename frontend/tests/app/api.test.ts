import { describe, expect, it, vi } from "vitest";

import { askQuestion, deleteRepository, ingestZip, listRepositories } from "../../src/app/api";
import { ApiError } from "../../src/app/types";

describe("api client", () => {
  it("maps ingest failure details to ApiError", async () => {
    const fetcher = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "archive is malformed" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      }),
    );
    const file = new File(["PK"], "repo.zip", { type: "application/zip" });
    await expect(ingestZip(file, { fetcher })).rejects.toEqual(
      expect.objectContaining({
        name: "ApiError",
        status: 400,
        message: "archive is malformed",
      }),
    );
    expect(ApiError).toBeDefined();
  });

  it("maps question JSON into camelCase citations", async () => {
    const fetcher = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          text: "found it",
          insufficient_evidence: true,
          citations: [],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    const answer = await askQuestion("repo-1", "Where?", { fetcher });
    expect(answer.insufficientEvidence).toBe(true);
    expect(answer.citations).toEqual([]);
  });

  it("maps repository list payloads", async () => {
    const fetcher = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          repositories: [
            {
              repository_id: "repo-1",
              status: "completed",
              indexed_file_count: 2,
              ignored_file_count: 0,
              indexed_paths: ["a.py"],
              ignored_reason_counts: [],
              failure_code: null,
              source_filename: "demo.zip",
              repository_card: {
                display_name: "demo",
                readme_path: "README.md",
                readme_excerpt: "# Demo",
                manifest_name: null,
                manifest_description: null,
                dependencies: [],
                languages: [{ language: "python", count: 1 }],
                outline_paths: ["a.py"],
                outline_truncated: false,
              },
            },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    const repos = await listRepositories({ fetcher });
    expect(repos).toEqual([
      expect.objectContaining({
        repositoryId: "repo-1",
        sourceFilename: "demo.zip",
        indexedFileCount: 2,
        card: expect.objectContaining({
          displayName: "demo",
          outlinePaths: ["a.py"],
        }),
      }),
    ]);
  });

  it("deletes a repository by id", async () => {
    const fetcher = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    await deleteRepository("repo-1", { fetcher });
    expect(fetcher).toHaveBeenCalledWith(
      expect.stringContaining("/api/repositories/repo-1"),
      expect.objectContaining({ method: "DELETE" }),
    );
  });
});
