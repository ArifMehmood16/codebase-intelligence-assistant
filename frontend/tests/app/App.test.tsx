import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../../src/app/App";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  sessionStorage.clear();
});

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function completedRepo(overrides: Record<string, unknown> = {}) {
  return {
    repository_id: "repo-1",
    status: "completed",
    indexed_file_count: 1,
    ignored_file_count: 1,
    indexed_paths: ["src/app.py"],
    ignored_reason_counts: [{ reason: "secret_file", count: 1 }],
    failure_code: null,
    source_filename: "repo.zip",
    ...overrides,
  };
}

function stubApi(
  handler: (url: string, init?: RequestInit) => Response | Promise<Response>,
) {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      return Promise.resolve(handler(url, init));
    }),
  );
}

async function waitForSelectedRepo(name: string) {
  expect(
    await screen.findByRole("heading", { name }),
  ).toBeInTheDocument();
}

describe("application shell", () => {
  it("shows the product name in the sidebar", async () => {
    stubApi(() => jsonResponse({ repositories: [] }));
    render(<App />);
    expect(await screen.findByText("Codebase Assistant")).toBeInTheDocument();
  });

  it("opens ingest modal from New repository", async () => {
    stubApi(() => jsonResponse({ repositories: [] }));
    render(<App />);
    const sidebar = await screen.findByLabelText("Indexed repositories");
    const newButtons = screen.getAllByRole("button", { name: "New repository" });
    fireEvent.click(newButtons[0]!);
    expect(
      screen.getByRole("heading", { name: "New repository" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Repository ZIP")).toBeInTheDocument();
    expect(sidebar).toBeInTheDocument();
  });

  it("lists repositories by derived name without showing a raw hash as the title", async () => {
    stubApi((url) => {
      if (url.endsWith("/api/repositories")) {
        return jsonResponse({
          repositories: [
            completedRepo({
              repository_id: "aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee",
              source_filename: "spring-petclinic.zip",
            }),
          ],
        });
      }
      return jsonResponse(completedRepo());
    });
    render(<App />);
    await waitForSelectedRepo("spring-petclinic");
    const list = screen.getByLabelText("Indexed repositories");
    expect(within(list).getByText("spring-petclinic")).toBeInTheDocument();
    expect(screen.queryByText(/aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee/)).toBeNull();
    expect(within(list).getByText("aaaa1111")).toBeInTheDocument();
  });

  it("does not restore a leftover searching spinner after reload", async () => {
    sessionStorage.setItem(
      "cia.chatByRepo.v1",
      JSON.stringify({
        "repo-1": [
          {
            id: "u1",
            role: "user",
            content: "what is this repo about?",
            createdAt: 1,
          },
          {
            id: "a1",
            role: "assistant",
            content: "",
            createdAt: 2,
            pending: true,
            statusLine: "Searching 87 files…",
          },
        ],
      }),
    );
    stubApi((url) => {
      if (url.endsWith("/api/repositories")) {
        return jsonResponse({
          repositories: [completedRepo({ indexed_file_count: 87 })],
        });
      }
      return jsonResponse(completedRepo({ indexed_file_count: 87 }));
    });
    render(<App />);
    expect(
      await screen.findByText("what is this repo about?"),
    ).toBeInTheDocument();
    expect(screen.queryByText(/Searching 87 files/)).toBeNull();
    expect(
      screen.getByText("The previous search was interrupted. Retry to ask again."),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });

  it("keeps chat history across questions for a repository", async () => {
    stubApi((url, init) => {
      if (url.endsWith("/api/repositories") && !init?.method) {
        return jsonResponse({ repositories: [completedRepo()] });
      }
      if (url.includes("/questions")) {
        return jsonResponse({
          text: "answer text",
          insufficient_evidence: false,
          citations: [
            {
              file_path: "src/app.py",
              start_line: 1,
              end_line: 2,
              excerpt: "def greet():\n    return 1\n",
            },
          ],
        });
      }
      return jsonResponse(completedRepo());
    });
    render(<App />);
    await waitForSelectedRepo("repo");
    const input = screen.getByRole("textbox", { name: "Message" });
    fireEvent.change(input, { target: { value: "First question?" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    await waitFor(() => {
      expect(screen.getByText("First question?")).toBeInTheDocument();
      expect(screen.getByText("answer text")).toBeInTheDocument();
    });
    fireEvent.change(screen.getByRole("textbox", { name: "Message" }), {
      target: { value: "Second question?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    await waitFor(() => {
      expect(screen.getByText("Second question?")).toBeInTheDocument();
    });
    expect(screen.getByText("First question?")).toBeInTheDocument();
  });

  it("shows citations with file and lines and a copyable code block", async () => {
    stubApi((url, init) => {
      if (url.endsWith("/api/repositories") && !init?.method) {
        return jsonResponse({ repositories: [completedRepo()] });
      }
      if (url.includes("/questions")) {
        return jsonResponse({
          text: "greet is defined [1]",
          insufficient_evidence: false,
          citations: [
            {
              file_path: "src/app.py",
              start_line: 1,
              end_line: 2,
              excerpt: '<script>alert("xss")</script>\ndef greet():\n',
            },
          ],
        });
      }
      return jsonResponse(completedRepo());
    });
    render(<App />);
    await waitForSelectedRepo("repo");
    expect(
      screen.queryByRole("button", { name: "Where is list_items defined?" }),
    ).toBeNull();
    fireEvent.click(
      screen.getByRole("button", { name: "Where is src/app.py implemented?" }),
    );
    await waitFor(() => {
      expect(screen.getByText(/greet is defined/)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /src\/app\.py/i }));
    expect(screen.getByText(/Lines 1–2/)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Copy source excerpt" }),
    ).toBeInTheDocument();
    expect(document.querySelector("pre code")).toHaveTextContent(
      '<script>alert("xss")</script>',
    );
    expect(document.querySelector("pre code")?.querySelector("script")).toBeNull();
  });

  it("suggests list_items only when handlers.py is indexed", async () => {
    stubApi((url) => {
      if (url.endsWith("/api/repositories")) {
        return jsonResponse({
          repositories: [
            completedRepo({
              indexed_paths: ["README.md", "src/api/handlers.py"],
              repository_card: {
                display_name: "fixture-repository",
                readme_path: "README.md",
                readme_excerpt: "# Inventory",
                manifest_name: null,
                manifest_description: null,
                dependencies: [],
                languages: [{ language: "python", count: 1 }],
                outline_paths: ["README.md", "src/api/handlers.py"],
                outline_truncated: false,
                declared_dependencies: [],
                endpoints: [
                  {
                    method: "GET",
                    path: "/items",
                    file_path: "src/api/handlers.py",
                    start_line: 10,
                    end_line: 10,
                  },
                ],
              },
            }),
          ],
        });
      }
      return jsonResponse(completedRepo());
    });
    render(<App />);
    await waitForSelectedRepo("repo");
    expect(
      screen.getByRole("button", { name: "Where is list_items defined?" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "What API endpoints exist?" }),
    ).toBeInTheDocument();
  });

  it("shows indexed files as a directory tree in the right-hand panel", async () => {
    stubApi((url) => {
      if (url.endsWith("/api/repositories")) {
        return jsonResponse({
          repositories: [
            completedRepo({
              indexed_file_count: 3,
              indexed_paths: ["README.md", "src/api/handlers.py", "src/app.py"],
            }),
          ],
        });
      }
      return jsonResponse(
        completedRepo({
          indexed_file_count: 3,
          indexed_paths: ["README.md", "src/api/handlers.py", "src/app.py"],
        }),
      );
    });
    render(<App />);
    await waitForSelectedRepo("repo");
    const panel = screen.getByRole("region", { name: "Indexed files" });
    expect(within(panel).getByText("src")).toBeInTheDocument();
    expect(within(panel).getByText("api")).toBeInTheDocument();
    expect(within(panel).getByTitle("README.md")).toHaveTextContent("README.md");
    expect(within(panel).getByTitle("src/app.py")).toHaveTextContent("app.py");
    expect(within(panel).getByTitle("src/api/handlers.py")).toHaveTextContent(
      "handlers.py",
    );
  });

  it("shows a visible delete control for the selected repository without opening a menu", async () => {
    stubApi((url) => {
      if (url.endsWith("/api/repositories")) {
        return jsonResponse({ repositories: [completedRepo()] });
      }
      return jsonResponse(completedRepo());
    });
    render(<App />);
    await waitForSelectedRepo("repo");
    expect(
      screen.getByRole("button", { name: "Delete repository" }),
    ).toBeInTheDocument();
  });

  it("opens the indexed files drawer from the repo menu", async () => {
    stubApi((url) => {
      if (url.endsWith("/api/repositories")) {
        return jsonResponse({ repositories: [completedRepo()] });
      }
      return jsonResponse(completedRepo());
    });
    render(<App />);
    await waitForSelectedRepo("repo");
    fireEvent.click(screen.getByRole("button", { name: "Repository actions" }));
    fireEvent.click(await screen.findByText("View indexed files"));
    const drawer = await screen.findByRole("dialog", { name: "Repository files" });
    expect(within(drawer).getByTitle("src/app.py")).toHaveTextContent("app.py");
  });
});
