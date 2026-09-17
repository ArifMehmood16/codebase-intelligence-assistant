import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ChatThread } from "../../src/app/components/ChatThread";
import type { ChatMessage, Repository } from "../../src/app/types";

const repository: Repository = {
  repositoryId: "repo-1",
  status: "completed",
  indexedFileCount: 2,
  ignoredFileCount: 0,
  indexedPaths: ["README.md", "src/OwnerController.java"],
  ignoredReasonCounts: [],
  failureCode: null,
  sourceFilename: "petclinic.zip",
  card: null,
};

function props(overrides: Partial<Parameters<typeof ChatThread>[0]> = {}) {
  return {
    repository,
    messages: [] as ChatMessage[],
    isAsking: false,
    askError: null,
    onSend: vi.fn(),
    onRetry: vi.fn(),
    onStop: vi.fn(),
    onClearError: vi.fn(),
    onOpenIngest: vi.fn(),
    ...overrides,
  };
}

describe("chat thread states", () => {
  it("opens ingestion when no repository is selected", () => {
    const view = props({ repository: null });
    render(<ChatThread {...view} />);
    expect(screen.getByRole("heading", { name: "Select a repository" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Ingest a ZIP" }));
    expect(view.onOpenIngest).toHaveBeenCalledOnce();
  });

  it("explains when a repository is not ready", () => {
    render(
      <ChatThread
        {...props({ repository: { ...repository, status: "indexing" } })}
      />,
    );
    expect(screen.getByText(/not ready for questions.*indexing/i)).toBeInTheDocument();
    expect(screen.queryByRole("textbox", { name: "Message" })).toBeNull();
  });

  it("submits starter and typed questions", () => {
    const view = props();
    render(<ChatThread {...view} />);
    fireEvent.click(screen.getByRole("button", { name: "What does this repo do?" }));
    expect(view.onSend).toHaveBeenCalledWith("What does this repo do?");

    const input = screen.getByRole("textbox", { name: "Message" });
    fireEvent.change(input, { target: { value: "  Trace controller flow  " } });
    fireEvent.keyDown(input, { key: "Enter", shiftKey: false });
    expect(view.onSend).toHaveBeenCalledWith("Trace controller flow");
  });

  it("supports stop, error dismissal and jumping to the latest message", () => {
    const view = props({
      messages: [
        {
          id: "user-1",
          role: "user",
          content: "Trace the flow",
          createdAt: 1,
        },
      ],
      isAsking: true,
      askError: "Provider unavailable",
    });
    const { container } = render(<ChatThread {...view} />);
    fireEvent.click(screen.getByRole("button", { name: "Stop" }));
    expect(view.onStop).toHaveBeenCalledOnce();
    fireEvent.click(screen.getByRole("button", { name: "Dismiss" }));
    expect(view.onClearError).toHaveBeenCalledOnce();

    const scroller = container.querySelector(".chat-scroll");
    expect(scroller).not.toBeNull();
    Object.defineProperties(scroller!, {
      scrollHeight: { configurable: true, value: 1000 },
      clientHeight: { configurable: true, value: 100 },
      scrollTop: { configurable: true, writable: true, value: 0 },
    });
    fireEvent.scroll(scroller!);
    fireEvent.click(screen.getByRole("button", { name: "Jump to latest" }));
    expect(scroller).toHaveProperty("scrollTop", 1000);
  });
});
