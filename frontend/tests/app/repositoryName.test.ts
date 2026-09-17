import { describe, expect, it } from "vitest";

import type { Repository } from "../../src/app/types";
import { repositoryDisplayName, repositoryNameKey } from "../../src/app/types";

function summary(partial: Partial<Repository>): Repository {
  return {
    repositoryId: "repo-1",
    status: "completed",
    indexedFileCount: 1,
    ignoredFileCount: 0,
    indexedPaths: [],
    ignoredReasonCounts: [],
    failureCode: null,
    sourceFilename: null,
    card: null,
    ...partial,
  };
}

describe("repositoryDisplayName", () => {
  it("uses the upload filename without .zip", () => {
    expect(
      repositoryDisplayName(summary({ sourceFilename: "petclinic.zip" })),
    ).toBe("petclinic");
  });

  it("falls back to a shared top-level folder from indexed paths", () => {
    expect(
      repositoryDisplayName(
        summary({
          sourceFilename: null,
          indexedPaths: [
            "spring-petclinic-main/README.md",
            "spring-petclinic-main/pom.xml",
          ],
        }),
      ),
    ).toBe("spring-petclinic-main");
  });

  it("does not show a repository id hash as the title", () => {
    expect(
      repositoryDisplayName(
        summary({
          repositoryId: "21552728-f42e-46ba-9701-3eb5a241852d",
          sourceFilename: null,
          indexedPaths: [],
        }),
      ),
    ).toBe("Untitled repository");
  });
});

describe("repositoryNameKey", () => {
  it("treats zip basename as case-insensitive unique key", () => {
    expect(repositoryNameKey(summary({ sourceFilename: "Demo.ZIP" }))).toBe(
      "demo",
    );
    expect(repositoryNameKey("demo.zip")).toBe("demo");
  });
});
