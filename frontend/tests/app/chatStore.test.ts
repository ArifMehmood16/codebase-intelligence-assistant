import { describe, expect, it } from "vitest";

import {
  CHAT_STORAGE_KEY,
  INTERRUPTED_SEARCH,
  loadStore,
  reviveStoredMessages,
} from "../../src/app/chatStore";
import type { ChatMessage } from "../../src/app/types";

describe("reviveStoredMessages", () => {
  it("turns leftover pending searches into a retryable error", () => {
    const stored: ChatMessage[] = [
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
    ];
    const revived = reviveStoredMessages(stored);
    expect(revived[0]).toEqual(stored[0]);
    expect(revived[1]?.pending).toBeUndefined();
    expect(revived[1]?.statusLine).toBeUndefined();
    expect(revived[1]?.error).toBe(INTERRUPTED_SEARCH);
  });

  it("leaves completed answers unchanged", () => {
    const stored: ChatMessage[] = [
      {
        id: "a1",
        role: "assistant",
        content: "It is an inventory service.",
        createdAt: 1,
        citations: [],
      },
    ];
    expect(reviveStoredMessages(stored)).toEqual(stored);
  });

  it("revives pending threads when loading session storage", () => {
    sessionStorage.setItem(
      CHAT_STORAGE_KEY,
      JSON.stringify({
        "repo-1": [
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
    const store = loadStore();
    expect(store["repo-1"]?.[0]?.pending).toBeUndefined();
    expect(store["repo-1"]?.[0]?.error).toBe(INTERRUPTED_SEARCH);
  });
});
