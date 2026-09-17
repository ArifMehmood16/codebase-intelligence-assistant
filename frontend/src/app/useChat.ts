import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { askQuestion } from "./api";
import { loadStore, saveStore } from "./chatStore";
import type { ChatMessage, Repository } from "./types";

function newId(): string {
  return crypto.randomUUID();
}

export type UseChatResult = {
  messages: ChatMessage[];
  isAsking: boolean;
  askError: string | null;
  send: (text: string) => Promise<void>;
  retry: (assistantMessageId: string) => Promise<void>;
  stop: () => void;
  clearError: () => void;
  clearThread: () => void;
  clearThreadFor: (repositoryId: string) => void;
};

export function useChat(repository: Repository | null): UseChatResult {
  const [store, setStore] = useState<Record<string, ChatMessage[]>>(loadStore);
  const [isAsking, setIsAsking] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const repositoryId = repository?.repositoryId ?? null;

  useEffect(() => {
    saveStore(store);
  }, [store]);

  const messages = useMemo(
    () => (repositoryId ? (store[repositoryId] ?? []) : []),
    [store, repositoryId],
  );

  const setMessagesForRepo = useCallback(
    (
      repoId: string,
      updater: (prev: ChatMessage[]) => ChatMessage[],
    ) => {
      setStore((prev) => ({
        ...prev,
        [repoId]: updater(prev[repoId] ?? []),
      }));
    },
    [],
  );

  const stop = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  const clearError = useCallback(() => setAskError(null), []);

  const clearThread = useCallback(() => {
    if (!repositoryId) {
      return;
    }
    setStore((prev) => {
      const next = { ...prev };
      delete next[repositoryId];
      return next;
    });
  }, [repositoryId]);

  const clearThreadFor = useCallback((targetId: string) => {
    setStore((prev) => {
      if (!(targetId in prev)) {
        return prev;
      }
      const next = { ...prev };
      delete next[targetId];
      return next;
    });
  }, []);

  const runAsk = useCallback(
    async (repo: Repository, question: string, priorUserId?: string) => {
      setAskError(null);
      setIsAsking(true);
      const controller = new AbortController();
      abortRef.current = controller;

      const userMessage: ChatMessage = {
        id: priorUserId ?? newId(),
        role: "user",
        content: question,
        createdAt: Date.now(),
      };
      const pendingId = newId();
      const pending: ChatMessage = {
        id: pendingId,
        role: "assistant",
        content: "",
        createdAt: Date.now(),
        pending: true,
        statusLine: `Searching ${repo.indexedFileCount} files…`,
      };

      setMessagesForRepo(repo.repositoryId, (prev) => {
        const withoutPending = prev.filter((m) => !m.pending);
        const hasUser = withoutPending.some((m) => m.id === userMessage.id);
        return [
          ...(hasUser ? withoutPending : [...withoutPending, userMessage]),
          pending,
        ];
      });

      try {
        const answer = await askQuestion(repo.repositoryId, question, {
          signal: controller.signal,
        });
        setMessagesForRepo(repo.repositoryId, (prev) =>
          prev.map((m) =>
            m.id === pendingId
              ? {
                  id: pendingId,
                  role: "assistant",
                  content: answer.text,
                  createdAt: Date.now(),
                  citations: answer.citations,
                  insufficientEvidence: answer.insufficientEvidence,
                }
              : m,
          ),
        );
      } catch (error) {
        const aborted =
          (error instanceof DOMException && error.name === "AbortError") ||
          (error instanceof Error && error.name === "AbortError");
        if (aborted) {
          setMessagesForRepo(repo.repositoryId, (prev) =>
            prev.filter((m) => m.id !== pendingId),
          );
          return;
        }
        const message =
          error instanceof Error ? error.message : "Question failed";
        setAskError(message);
        setMessagesForRepo(repo.repositoryId, (prev) =>
          prev.map((m) =>
            m.id === pendingId
              ? {
                  id: pendingId,
                  role: "assistant",
                  content: "",
                  createdAt: Date.now(),
                  error: message,
                }
              : m,
          ),
        );
      } finally {
        setIsAsking(false);
        abortRef.current = null;
      }
    },
    [setMessagesForRepo],
  );

  const send = useCallback(
    async (text: string) => {
      if (!repository || !text.trim() || isAsking) {
        return;
      }
      await runAsk(repository, text.trim());
    },
    [repository, isAsking, runAsk],
  );

  const retry = useCallback(
    async (assistantMessageId: string) => {
      if (!repository || isAsking) {
        return;
      }
      const thread = store[repository.repositoryId] ?? [];
      const index = thread.findIndex((m) => m.id === assistantMessageId);
      if (index < 1) {
        return;
      }
      const prior = thread[index - 1];
      if (prior?.role !== "user") {
        return;
      }
      setMessagesForRepo(repository.repositoryId, (prev) =>
        prev.filter((m) => m.id !== assistantMessageId),
      );
      await runAsk(repository, prior.content, prior.id);
    },
    [repository, isAsking, store, setMessagesForRepo, runAsk],
  );

  return {
    messages,
    isAsking,
    askError,
    send,
    retry,
    stop,
    clearError,
    clearThread,
    clearThreadFor,
  };
}
