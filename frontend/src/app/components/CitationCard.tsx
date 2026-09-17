import { useId, useState } from "react";
import Button from "react-bootstrap/Button";
import Collapse from "react-bootstrap/Collapse";

import type { Citation } from "../types";
import { truncatePathLeft } from "../types";

type CitationCardProps = {
  index: number;
  citation: Citation;
  highlighted: boolean;
  cardRef?: (node: HTMLDivElement | null) => void;
};

export function CitationCard({
  index,
  citation,
  highlighted,
  cardRef,
}: CitationCardProps) {
  const [open, setOpen] = useState(false);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);
  const collapseId = useId();
  const label = truncatePathLeft(citation.filePath);

  async function copyExcerpt() {
    try {
      await navigator.clipboard.writeText(citation.excerpt);
      setCopyStatus("Copied");
      window.setTimeout(() => setCopyStatus(null), 1500);
    } catch {
      setCopyStatus("Copy failed");
    }
  }

  const lines = citation.excerpt.split("\n");

  return (
    <div
      ref={cardRef}
      id={`citation-${index}`}
      className={`citation-card ${highlighted ? "is-highlighted" : ""}`}
    >
      <button
        type="button"
        className="citation-card-header"
        aria-expanded={open}
        aria-controls={collapseId}
        onClick={() => setOpen((value) => !value)}
      >
        <span className="citation-index">[{index}]</span>
        <span className="citation-path font-monospace text-truncate" title={citation.filePath}>
          {label}
        </span>
        <span className="citation-lines text-muted">
          Lines {citation.startLine}–{citation.endLine}
        </span>
      </button>
      <Collapse in={open}>
        <div id={collapseId}>
          <div className="citation-body">
            <div className="code-window">
              <div className="code-window-header">
                <span className="small text-truncate">{citation.filePath}</span>
                <Button
                  type="button"
                  size="sm"
                  variant="outline-light"
                  aria-label="Copy source excerpt"
                  onClick={() => void copyExcerpt()}
                >
                  Copy
                </Button>
              </div>
              <pre className="excerpt-pre mb-0">
                <code>
                  {lines.map((line, lineIndex) => (
                    <span key={`${citation.filePath}-${lineIndex}`} className="code-line">
                      <span className="line-number" aria-hidden>
                        {citation.startLine + lineIndex}
                      </span>
                      <span className="line-text">{line || " "}</span>
                      {"\n"}
                    </span>
                  ))}
                </code>
              </pre>
            </div>
            {copyStatus ? (
              <p className="small mb-0 mt-2" role="status">
                {copyStatus}
              </p>
            ) : null}
          </div>
        </div>
      </Collapse>
    </div>
  );
}
