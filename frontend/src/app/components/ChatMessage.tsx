import { useMemo, useRef, useState } from "react";
import Button from "react-bootstrap/Button";
import Spinner from "react-bootstrap/Spinner";

import type { ChatMessage } from "../types";
import { CitationCard } from "./CitationCard";
import { MarkdownAnswer } from "./MarkdownAnswer";

type ChatMessageViewProps = {
  message: ChatMessage;
  onRetry?: (messageId: string) => void;
};

export function ChatMessageView({ message, onRetry }: ChatMessageViewProps) {
  const [highlight, setHighlight] = useState<number | null>(null);
  const cardRefs = useRef<Record<number, HTMLDivElement | null>>({});
  const citations = message.citations ?? [];

  const body = useMemo(
    () =>
      message.role === "assistant" && !message.pending && !message.error
        ? (
            <MarkdownAnswer
              text={message.content}
              citationCount={citations.length}
              onCitationClick={(index) => {
                setHighlight(index);
                cardRefs.current[index]?.scrollIntoView({
                  behavior: "smooth",
                  block: "nearest",
                });
              }}
            />
          )
        : null,
    [message, citations.length],
  );

  if (message.role === "user") {
    return (
      <div className="chat-row chat-row-user">
        <div className="chat-bubble-user">{message.content}</div>
      </div>
    );
  }

  if (message.pending) {
    return (
      <div className="chat-row chat-row-assistant" aria-live="polite">
        <div className="assistant-skeleton">
          <div className="d-flex align-items-center gap-2 mb-2">
            <Spinner animation="border" size="sm" />
            <span className="text-muted small">{message.statusLine ?? "Working…"}</span>
          </div>
          <div className="skeleton-line" />
          <div className="skeleton-line short" />
        </div>
      </div>
    );
  }

  if (message.error) {
    return (
      <div className="chat-row chat-row-assistant">
        <div className="assistant-error" role="alert">
          <div>{message.error}</div>
          {onRetry ? (
            <Button
              type="button"
              size="sm"
              variant="outline-secondary"
              className="mt-2"
              onClick={() => onRetry(message.id)}
            >
              Retry
            </Button>
          ) : null}
        </div>
      </div>
    );
  }

  return (
    <div className="chat-row chat-row-assistant chat-row-hoverable">
      <div className="assistant-actions">
        <Button
          type="button"
          size="sm"
          variant="outline-secondary"
          aria-label="Copy answer"
          onClick={() => void navigator.clipboard.writeText(message.content)}
        >
          Copy
        </Button>
        {onRetry ? (
          <Button
            type="button"
            size="sm"
            variant="outline-secondary"
            aria-label="Retry answer"
            onClick={() => onRetry(message.id)}
          >
            Retry
          </Button>
        ) : null}
      </div>
      {message.insufficientEvidence ? (
        <div className="insufficient-callout">
          <span className="insufficient-icon" aria-hidden>
            i
          </span>
          <div>
            <div className="fw-semibold">Insufficient evidence</div>
            <div className="text-muted small">
              The retrieved sources do not support a grounded answer.
            </div>
          </div>
        </div>
      ) : null}
      {message.content ? (
        <div className="assistant-prose">{body ?? message.content}</div>
      ) : null}
      {citations.length > 0 ? (
        <div className="citation-list mt-3" aria-label="Citations">
          {citations.map((citation, offset) => {
            const index = offset + 1;
            return (
              <CitationCard
                key={`${citation.filePath}:${citation.startLine}:${index}`}
                index={index}
                citation={citation}
                highlighted={highlight === index}
                cardRef={(node) => {
                  cardRefs.current[index] = node;
                }}
              />
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
