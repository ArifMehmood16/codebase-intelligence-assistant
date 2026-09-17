import { fireEvent, render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ChatMessageView } from "../../src/app/components/ChatMessage";
import type { ChatMessage } from "../../src/app/types";

beforeEach(() => {
  Element.prototype.scrollIntoView = vi.fn();
});

function assistantMessage(content: string): ChatMessage {
  return {
    id: "answer-1",
    role: "assistant",
    content,
    createdAt: 1,
    citations: [
      {
        filePath: "README.md",
        startLine: 1,
        endLine: 2,
        excerpt: "# Inventory\n<script>alert('source')</script>",
      },
    ],
  };
}

describe("assistant Markdown answers", () => {
  it("renders a directory tree as an escaped, labelled card", () => {
    render(
      <ChatMessageView
        message={assistantMessage(
          "Bounded indexed outline.\n\n" +
            "### Directory structure\n\n" +
            "```tree\nsrc/\n  <script>alert('tree')</script>\n  app.py\n```\n\n" +
            "README context [1]",
        )}
      />,
    );

    expect(
      screen.getByRole("heading", { level: 3, name: "Directory structure" }),
    ).toBeInTheDocument();
    const tree = screen.getByRole("region", { name: "Directory structure" });
    expect(within(tree).getByText(/src\//)).toHaveTextContent("app.py");
    expect(tree.querySelector("script")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "[1]" }));
    expect(document.querySelector(".citation-card.is-highlighted")).not.toBeNull();
  });

  it("renders simple lists, emphasis and inline code without raw HTML", () => {
    const { container } = render(
      <ChatMessageView
        message={assistantMessage(
          "### OwnerController\n\n" +
            "- **Flow:** `OwnerController.save` → `OwnerRepository.save` [1]\n" +
            "- <img src=x onerror=alert(1)> remains text",
        )}
      />,
    );

    expect(screen.getByRole("heading", { name: "OwnerController" })).toBeInTheDocument();
    expect(screen.getAllByRole("listitem")).toHaveLength(2);
    expect(screen.getByText("Flow:").tagName).toBe("STRONG");
    expect(screen.getByText("OwnerController.save").tagName).toBe("CODE");
    expect(container.querySelector("img")).toBeNull();
  });

  it("renders ordered lists, supported heading levels and generic code cards", () => {
    render(
      <ChatMessageView
        message={assistantMessage(
          "# Flow report\n\n" +
            "## Layers\n\n" +
            "#### Notes\n\n" +
            "1. Controller\n2. Repository [9]\n\n" +
            "```java\nclass Owner {}\n```\n\n" +
            "```\nunlabelled\n```\n\n" +
            "A multiline paragraph\ncontinues on the next line.",
        )}
      />,
    );

    expect(screen.getByRole("heading", { level: 1, name: "Flow report" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 2, name: "Layers" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 4, name: "Notes" })).toBeInTheDocument();
    const items = screen.getAllByRole("listitem");
    expect(items).toHaveLength(2);
    expect(items[1]).toHaveTextContent("Repository [9]");
    expect(screen.getByRole("region", { name: "java code" })).toHaveTextContent(
      "class Owner",
    );
    expect(screen.getByRole("region", { name: "Code block" })).toHaveTextContent(
      "unlabelled",
    );
    expect(screen.getByText(/A multiline paragraph continues/)).toBeInTheDocument();
  });

  it("renders an escaped controller-method table with interactive citations", () => {
    const { container } = render(
      <ChatMessageView
        message={assistantMessage(
          "VisitController prepares and saves visits.\n\n" +
            "| Method | Route / trigger | Purpose | Collaborators / entities |\n" +
            "| --- | --- | --- | --- |\n" +
            "| loadPetWithVisit | model setup | Loads `<script>alert(1)</script>` | Owner [1] |\n" +
            "| processNewVisitForm | POST | Saves a visit | VisitRepository |",
        )}
      />,
    );

    const table = screen.getByRole("table");
    expect(within(table).getAllByRole("columnheader")).toHaveLength(4);
    expect(within(table).getAllByRole("row")).toHaveLength(3);
    expect(within(table).getByText("loadPetWithVisit")).toBeInTheDocument();
    expect(container.querySelector("script")).toBeNull();

    fireEvent.click(within(table).getByRole("button", { name: "[1]" }));
    expect(document.querySelector(".citation-card.is-highlighted")).not.toBeNull();
  });

  it("renders user, pending, failure and insufficient-evidence states", () => {
    const onRetry = vi.fn();
    const { rerender } = render(
      <ChatMessageView
        message={{
          id: "user-1",
          role: "user",
          content: "Where is Owner?",
          createdAt: 1,
        }}
      />,
    );
    expect(screen.getByText("Where is Owner?")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Copy answer" })).toBeNull();

    rerender(
      <ChatMessageView
        message={{
          id: "pending-1",
          role: "assistant",
          content: "",
          createdAt: 2,
          pending: true,
          statusLine: "Tracing controllers…",
        }}
      />,
    );
    expect(screen.getByText("Tracing controllers…")).toBeInTheDocument();

    rerender(
      <ChatMessageView
        message={{
          id: "failed-1",
          role: "assistant",
          content: "",
          createdAt: 3,
          error: "The request failed",
        }}
        onRetry={onRetry}
      />,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("The request failed");
    fireEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledWith("failed-1");

    rerender(
      <ChatMessageView
        message={{
          id: "ie-1",
          role: "assistant",
          content: "Not enough source context.",
          createdAt: 4,
          insufficientEvidence: true,
        }}
      />,
    );
    expect(screen.getByText("Insufficient evidence")).toBeInTheDocument();
    expect(screen.getByText("Not enough source context.")).toBeInTheDocument();
  });
});
