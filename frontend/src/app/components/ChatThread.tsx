import { useEffect, useRef, useState } from "react";
import Button from "react-bootstrap/Button";

import type { ChatMessage, Repository } from "../types";
import { repositoryDisplayName } from "../types";
import { starterQuestions } from "../starterQuestions";
import { ChatMessageView } from "./ChatMessage";
import { Composer } from "./Composer";

type ChatThreadProps = {
  repository: Repository | null;
  messages: ChatMessage[];
  isAsking: boolean;
  askError: string | null;
  onSend: (text: string) => void;
  onRetry: (messageId: string) => void;
  onStop: () => void;
  onClearError: () => void;
  onOpenIngest: () => void;
};

export function ChatThread({
  repository,
  messages,
  isAsking,
  askError,
  onSend,
  onRetry,
  onStop,
  onClearError,
  onOpenIngest,
}: ChatThreadProps) {
  const scrollerRef = useRef<HTMLDivElement>(null);
  const [stickToBottom, setStickToBottom] = useState(true);
  const [showJump, setShowJump] = useState(false);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el || !stickToBottom) {
      setShowJump(!stickToBottom && messages.length > 0);
      return;
    }
    el.scrollTop = el.scrollHeight;
    setShowJump(false);
  }, [messages, stickToBottom, isAsking]);

  function onScroll() {
    const el = scrollerRef.current;
    if (!el) {
      return;
    }
    const distance = el.scrollHeight - el.scrollTop - el.clientHeight;
    const nearBottom = distance < 80;
    setStickToBottom(nearBottom);
    setShowJump(!nearBottom);
  }

  function jumpToLatest() {
    const el = scrollerRef.current;
    if (!el) {
      return;
    }
    el.scrollTop = el.scrollHeight;
    setStickToBottom(true);
    setShowJump(false);
  }

  if (!repository) {
    return (
      <div className="chat-empty h-100 d-flex flex-column align-items-center justify-content-center text-center px-3">
        <h2 className="h5 mb-2">Select a repository</h2>
        <p className="text-muted mb-3">
          Choose one from the sidebar, or ingest a ZIP to start asking questions.
        </p>
        <Button type="button" onClick={onOpenIngest}>
          Ingest a ZIP
        </Button>
      </div>
    );
  }

  if (repository.status !== "completed") {
    return (
      <div className="chat-empty h-100 d-flex flex-column align-items-center justify-content-center text-center px-3">
        <h2 className="h5 mb-2">{repositoryDisplayName(repository)}</h2>
        <p className="text-muted mb-0">
          This repository is not ready for questions (status: {repository.status}
          ).
        </p>
      </div>
    );
  }

  const empty = messages.length === 0;

  return (
    <div className="chat-thread d-flex flex-column h-100">
      <div
        className="chat-scroll flex-grow-1"
        ref={scrollerRef}
        onScroll={onScroll}
        aria-live="polite"
      >
        {empty ? (
          <div className="chat-empty-state">
            <h2 className="h4 mb-2">{repositoryDisplayName(repository)}</h2>
            <p className="text-muted mb-4">
              Ask a question about the indexed sources. Answers cite retrieved
              files.
            </p>
            <div className="starter-grid" aria-label="Suggested questions">
              {starterQuestions(repository).map((text) => (
                <button
                  key={text}
                  type="button"
                  className="starter-chip"
                  disabled={isAsking}
                  onClick={() => onSend(text)}
                >
                  {text}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map((message) => (
              <ChatMessageView
                key={message.id}
                message={message}
                onRetry={message.role === "assistant" ? onRetry : undefined}
              />
            ))}
          </div>
        )}
      </div>

      {showJump ? (
        <button type="button" className="jump-latest" onClick={jumpToLatest}>
          Jump to latest
        </button>
      ) : null}

      {askError ? (
        <div className="px-3 py-2 border-top" role="alert">
          <span className="text-danger small me-2">{askError}</span>
          <Button type="button" size="sm" variant="outline-secondary" onClick={onClearError}>
            Dismiss
          </Button>
        </div>
      ) : null}

      <Composer
        disabled={repository.status !== "completed"}
        busy={isAsking}
        onSend={onSend}
        onStop={onStop}
      />
    </div>
  );
}
