import type { ChatMessage } from "./types";

export const CHAT_STORAGE_KEY = "cia.chatByRepo.v1";

export const INTERRUPTED_SEARCH =
  "The previous search was interrupted. Retry to ask again.";

export function reviveStoredMessages(messages: ChatMessage[]): ChatMessage[] {
  return messages.map((message) => {
    if (message.role !== "assistant" || !message.pending) {
      return message;
    }
    return {
      id: message.id,
      role: "assistant",
      content: "",
      createdAt: message.createdAt,
      error: INTERRUPTED_SEARCH,
    };
  });
}

export function loadStore(): Record<string, ChatMessage[]> {
  try {
    const raw = sessionStorage.getItem(CHAT_STORAGE_KEY);
    if (!raw) {
      return {};
    }
    const parsed = JSON.parse(raw) as Record<string, ChatMessage[]>;
    if (!parsed || typeof parsed !== "object") {
      return {};
    }
    const revived: Record<string, ChatMessage[]> = {};
    for (const [repositoryId, messages] of Object.entries(parsed)) {
      if (Array.isArray(messages)) {
        revived[repositoryId] = reviveStoredMessages(messages);
      }
    }
    return revived;
  } catch {
    return {};
  }
}

export function saveStore(store: Record<string, ChatMessage[]>): void {
  try {
    const serializable: Record<string, ChatMessage[]> = {};
    for (const [repositoryId, messages] of Object.entries(store)) {
      serializable[repositoryId] = reviveStoredMessages(messages);
    }
    sessionStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(serializable));
  } catch {
    /* ignore quota */
  }
}
