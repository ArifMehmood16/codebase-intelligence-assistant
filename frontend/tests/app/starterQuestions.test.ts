import { describe, expect, it } from "vitest";

import { starterQuestions } from "../../src/app/starterQuestions";
import type { Repository, RepositoryCardView } from "../../src/app/types";

function repo(partial: Partial<Repository> = {}): Repository {
  return {
    repositoryId: "repo-1",
    status: "completed",
    indexedFileCount: 1,
    ignoredFileCount: 0,
    indexedPaths: [],
    ignoredReasonCounts: [],
    failureCode: null,
    sourceFilename: "repo.zip",
    card: null,
    ...partial,
  };
}

function card(partial: Partial<RepositoryCardView> = {}): RepositoryCardView {
  return {
    displayName: "repo",
    readmePath: null,
    readmeExcerpt: "",
    manifestName: null,
    manifestDescription: null,
    dependencies: [],
    languages: [],
    outlinePaths: [],
    outlineTruncated: false,
    declaredDependencies: [],
    endpoints: [],
    ...partial,
  };
}

describe("starterQuestions", () => {
  it("does not suggest list_items for a repo that only indexed src/app.py", () => {
    const chips = starterQuestions(repo({ indexedPaths: ["src/app.py"] }));
    expect(chips).toContain("What does this repo do?");
    expect(chips).toContain("What is the directory structure?");
    expect(chips).toContain("Where is src/app.py implemented?");
    expect(chips.join(" ")).not.toMatch(/list_items/);
    expect(chips.length).toBeGreaterThanOrEqual(3);
    expect(chips.length).toBeLessThanOrEqual(4);
  });

  it("suggests list_items when src/api/handlers.py is indexed", () => {
    const chips = starterQuestions(
      repo({
        indexedPaths: ["README.md", "src/api/handlers.py"],
        card: card({
          readmePath: "README.md",
          outlinePaths: ["README.md", "src/api/handlers.py"],
          endpoints: [
            {
              method: "GET",
              path: "/items",
              filePath: "src/api/handlers.py",
              startLine: 10,
              endLine: 10,
            },
          ],
        }),
      }),
    );
    expect(chips).toContain("Where is list_items defined?");
    expect(chips).toContain("What API endpoints exist?");
    expect(chips.length).toBeLessThanOrEqual(4);
  });

  it("suggests dependencies when the card lists declared packages", () => {
    const chips = starterQuestions(
      repo({
        indexedPaths: ["package.json", "src/app.py"],
        card: card({
          dependencies: ["react"],
          declaredDependencies: [
            {
              name: "react",
              filePath: "package.json",
              startLine: 1,
              endLine: 1,
            },
          ],
        }),
      }),
    );
    expect(chips).toContain("What dependencies does this project declare?");
  });
});
