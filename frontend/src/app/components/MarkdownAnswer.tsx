import type { ReactNode } from "react";

type MarkdownAnswerProps = {
  text: string;
  citationCount: number;
  onCitationClick: (index: number) => void;
};

type Block =
  | { kind: "heading"; level: number; text: string }
  | { kind: "paragraph"; text: string }
  | { kind: "list"; ordered: boolean; items: string[] }
  | { kind: "code"; language: string; text: string }
  | { kind: "table"; headers: string[]; rows: string[][] };

const INLINE_TOKEN = /(\[(\d+)\]|\*\*([^*]+)\*\*|`([^`\n]+)`)/g;

export function MarkdownAnswer({
  text,
  citationCount,
  onCitationClick,
}: MarkdownAnswerProps) {
  return parseBlocks(text).map((block, index) => {
    const key = `block-${index}`;
    if (block.kind === "heading") {
      const content = renderInline(
        block.text,
        citationCount,
        onCitationClick,
        key,
      );
      if (block.level === 1) return <h1 key={key}>{content}</h1>;
      if (block.level === 2) return <h2 key={key}>{content}</h2>;
      if (block.level === 3) return <h3 key={key}>{content}</h3>;
      return <h4 key={key}>{content}</h4>;
    }
    if (block.kind === "code") {
      const label =
        block.language.toLowerCase() === "tree"
          ? "Directory structure"
          : block.language
            ? `${block.language} code`
            : "Code block";
      return (
        <section key={key} className="markdown-code-card" aria-label={label}>
          <div className="markdown-code-card-header">{label}</div>
          <pre className="markdown-code-card-body">
            <code>{block.text}</code>
          </pre>
        </section>
      );
    }
    if (block.kind === "list") {
      const items = block.items.map((item, itemIndex) => (
        <li key={`${key}-item-${itemIndex}`}>
          {renderInline(
            item,
            citationCount,
            onCitationClick,
            `${key}-item-${itemIndex}`,
          )}
        </li>
      ));
      return block.ordered ? <ol key={key}>{items}</ol> : <ul key={key}>{items}</ul>;
    }
    if (block.kind === "table") {
      return (
        <div key={key} className="markdown-table-card">
          <table>
            <thead>
              <tr>
                {block.headers.map((header, cellIndex) => (
                  <th key={`${key}-head-${cellIndex}`} scope="col">
                    {renderInline(
                      header,
                      citationCount,
                      onCitationClick,
                      `${key}-head-${cellIndex}`,
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((row, rowIndex) => (
                <tr key={`${key}-row-${rowIndex}`}>
                  {row.map((cell, cellIndex) => (
                    <td key={`${key}-row-${rowIndex}-cell-${cellIndex}`}>
                      {renderInline(
                        cell,
                        citationCount,
                        onCitationClick,
                        `${key}-row-${rowIndex}-cell-${cellIndex}`,
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }
    return (
      <p key={key} className="assistant-paragraph">
        {renderInline(block.text, citationCount, onCitationClick, key)}
      </p>
    );
  });
}

function renderInline(
  text: string,
  citationCount: number,
  onCitationClick: (index: number) => void,
  keyPrefix: string,
): ReactNode[] {
  const parts: ReactNode[] = [];
  let last = 0;
  let key = 0;
  for (const match of text.matchAll(INLINE_TOKEN)) {
    const offset = match.index;
    if (offset > last) {
      parts.push(text.slice(last, offset));
    }
    const citationIndex = match[2] ? Number(match[2]) : null;
    if (
      citationIndex !== null &&
      citationIndex >= 1 &&
      citationIndex <= citationCount
    ) {
      parts.push(
        <button
          key={`${keyPrefix}-citation-${key++}`}
          type="button"
          className="citation-marker"
          onClick={() => onCitationClick(citationIndex)}
        >
          [{citationIndex}]
        </button>,
      );
    } else if (match[3] !== undefined) {
      parts.push(<strong key={`${keyPrefix}-strong-${key++}`}>{match[3]}</strong>);
    } else if (match[4] !== undefined) {
      parts.push(<code key={`${keyPrefix}-code-${key++}`}>{match[4]}</code>);
    } else {
      parts.push(match[0]);
    }
    last = offset + match[0].length;
  }
  if (last < text.length) {
    parts.push(text.slice(last));
  }
  return parts;
}

function parseBlocks(text: string): Block[] {
  const lines = text.replace(/\r\n?/g, "\n").split("\n");
  const blocks: Block[] = [];
  let index = 0;
  while (index < lines.length) {
    const line = lines[index] ?? "";
    if (!line.trim()) {
      index += 1;
      continue;
    }
    const fence = line.match(/^```([A-Za-z0-9_-]*)\s*$/);
    if (fence) {
      const content: string[] = [];
      index += 1;
      while (index < lines.length && !/^```\s*$/.test(lines[index] ?? "")) {
        content.push(lines[index] ?? "");
        index += 1;
      }
      if (index < lines.length) index += 1;
      blocks.push({
        kind: "code",
        language: fence[1] ?? "",
        text: content.join("\n"),
      });
      continue;
    }
    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      blocks.push({
        kind: "heading",
        level: heading[1]?.length ?? 4,
        text: heading[2] ?? "",
      });
      index += 1;
      continue;
    }
    const headers = parseTableRow(line);
    const delimiter = parseTableRow(lines[index + 1] ?? "");
    if (
      headers &&
      delimiter &&
      headers.length === delimiter.length &&
      delimiter.every((cell) => /^:?-{3,}:?$/.test(cell))
    ) {
      const rows: string[][] = [];
      index += 2;
      while (index < lines.length) {
        const row = parseTableRow(lines[index] ?? "");
        if (!row || row.length !== headers.length) break;
        rows.push(row);
        index += 1;
      }
      blocks.push({ kind: "table", headers, rows });
      continue;
    }
    const unordered = line.match(/^\s*[-*]\s+(.+)$/);
    const ordered = line.match(/^\s*\d+\.\s+(.+)$/);
    if (unordered || ordered) {
      const isOrdered = Boolean(ordered);
      const items: string[] = [];
      while (index < lines.length) {
        const candidate = lines[index] ?? "";
        const match = isOrdered
          ? candidate.match(/^\s*\d+\.\s+(.+)$/)
          : candidate.match(/^\s*[-*]\s+(.+)$/);
        if (!match) break;
        items.push(match[1] ?? "");
        index += 1;
      }
      blocks.push({ kind: "list", ordered: isOrdered, items });
      continue;
    }
    const paragraph = [line.trim()];
    index += 1;
    while (index < lines.length && !startsBlock(lines[index] ?? "")) {
      paragraph.push((lines[index] ?? "").trim());
      index += 1;
    }
    blocks.push({ kind: "paragraph", text: paragraph.filter(Boolean).join(" ") });
  }
  return blocks;
}

function startsBlock(line: string): boolean {
  return (
    !line.trim() ||
    /^```/.test(line) ||
    /^(#{1,4})\s+/.test(line) ||
    /^\s*\|.*\|\s*$/.test(line) ||
    /^\s*[-*]\s+/.test(line) ||
    /^\s*\d+\.\s+/.test(line)
  );
}

function parseTableRow(line: string): string[] | null {
  const trimmed = line.trim();
  if (!trimmed.startsWith("|") || !trimmed.endsWith("|")) return null;
  const cells = trimmed
    .slice(1, -1)
    .split("|")
    .map((cell) => cell.trim());
  return cells.length > 0 ? cells : null;
}
