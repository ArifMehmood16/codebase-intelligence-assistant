import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { IndexedFilePanel } from "../../src/app/components/IndexedFilePanel";
import type { Repository } from "../../src/app/types";

function repository(overrides: Partial<Repository> = {}): Repository {
  return {
    repositoryId: "repo-1",
    status: "completed",
    indexedFileCount: 3,
    ignoredFileCount: 0,
    indexedPaths: ["README.md", "src/api/handlers.py", "src/app.py"],
    ignoredReasonCounts: [],
    failureCode: null,
    sourceFilename: "petclinic.zip",
    card: null,
    ...overrides,
  };
}

describe("indexed file panel", () => {
  it("shows filenames with extensions in a directory tree and the full path on hover", () => {
    render(<IndexedFilePanel repository={repository()} />);

    const panel = screen.getByRole("region", { name: "Indexed files" });
    expect(within(panel).getByText("src")).toBeInTheDocument();
    expect(within(panel).getByText("api")).toBeInTheDocument();
    expect(within(panel).getByTitle("README.md")).toHaveTextContent("README.md");
    expect(within(panel).getByTitle("src/app.py")).toHaveTextContent("app.py");
    expect(within(panel).getByTitle("src/api/handlers.py")).toHaveTextContent(
      "handlers.py",
    );
  });

  it("keeps a long filename's extension visible and puts the full path on the hover title", () => {
    const longName = "SupercalifragilisticexpialidociousOwnerController.java";
    const path = `src/main/java/${longName}`;
    render(
      <IndexedFilePanel
        repository={repository({
          indexedFileCount: 1,
          indexedPaths: [path],
        })}
      />,
    );

    const file = screen.getByTitle(path);
    expect(file).toHaveTextContent(longName);
    expect(file.querySelector(".file-tree-ext")).toHaveTextContent(".java");
  });

  it("explains when no repository is selected", () => {
    render(<IndexedFilePanel repository={null} />);
    expect(
      screen.getByText("Select a repository to see indexed files."),
    ).toBeInTheDocument();
  });

  it("filters the tree to matching paths", () => {
    render(<IndexedFilePanel repository={repository()} />);
    fireEvent.change(screen.getByLabelText("Filter indexed files"), {
      target: { value: "handlers" },
    });
    const panel = screen.getByRole("region", { name: "Indexed files" });
    expect(within(panel).getByTitle("src/api/handlers.py")).toBeInTheDocument();
    expect(within(panel).queryByTitle("src/app.py")).toBeNull();
    expect(within(panel).queryByTitle("README.md")).toBeNull();
  });

  it("renders hostile path names as text", () => {
    render(
      <IndexedFilePanel
        repository={repository({
          indexedFileCount: 1,
          indexedPaths: ["src/<img src=x onerror=alert(1)>.py"],
        })}
      />,
    );
    expect(
      screen.getByTitle("src/<img src=x onerror=alert(1)>.py"),
    ).toHaveTextContent("<img src=x onerror=alert(1)>.py");
    expect(document.querySelector("img")).toBeNull();
  });
});
