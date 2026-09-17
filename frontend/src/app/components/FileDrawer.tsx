import { useMemo, useState } from "react";
import Form from "react-bootstrap/Form";
import Offcanvas from "react-bootstrap/Offcanvas";
import Tab from "react-bootstrap/Tab";
import Tabs from "react-bootstrap/Tabs";

import type { Repository } from "../types";
import { FileTreeView } from "./FileTree";

const PAGE_SIZE = 80;

type FileDrawerProps = {
  show: boolean;
  onHide: () => void;
  repository: Repository | null;
};

export function FileDrawer({ show, onHide, repository }: FileDrawerProps) {
  const [filter, setFilter] = useState("");
  const [tab, setTab] = useState<"indexed" | "ignored">("indexed");
  const [page, setPage] = useState(0);

  const indexed = useMemo(() => {
    const q = filter.trim().toLowerCase();
    const paths = repository?.indexedPaths ?? [];
    return q ? paths.filter((p) => p.toLowerCase().includes(q)) : paths;
  }, [repository, filter]);

  const ignoredRows = useMemo(() => {
    const rows =
      repository?.ignoredReasonCounts.map(
        (row) => `${row.reason} (${row.count})`,
      ) ?? [];
    const q = filter.trim().toLowerCase();
    return q ? rows.filter((r) => r.toLowerCase().includes(q)) : rows;
  }, [repository, filter]);

  const pageCount = Math.max(1, Math.ceil(ignoredRows.length / PAGE_SIZE));
  const ignoredPage = ignoredRows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  return (
    <Offcanvas
      show={show}
      onHide={onHide}
      placement="end"
      className="file-drawer"
      aria-labelledby="repo-files-label"
    >
      <Offcanvas.Header closeButton>
        <Offcanvas.Title id="repo-files-label">Repository files</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body className="d-flex flex-column">
        {!repository ? (
          <p className="text-muted">No repository selected.</p>
        ) : (
          <>
            <p className="text-muted small">
              Indexed {repository.indexedFileCount} · Ignored{" "}
              {repository.ignoredFileCount}
            </p>
            <Form.Control
              className="mb-3"
              type="search"
              placeholder="Filter…"
              value={filter}
              aria-label="Filter files"
              onChange={(event) => {
                setFilter(event.target.value);
                setPage(0);
              }}
            />
            <Tabs
              activeKey={tab}
              onSelect={(key) => {
                setTab(key === "ignored" ? "ignored" : "indexed");
                setPage(0);
              }}
              className="mb-2"
            >
              <Tab eventKey="indexed" title={`Indexed (${indexed.length})`} />
              <Tab
                eventKey="ignored"
                title={`Ignored (${repository.ignoredFileCount})`}
              />
            </Tabs>
            {tab === "ignored" ? (
              <p className="text-muted small">
                The API returns ignored reason counts, not individual ignored
                paths.
              </p>
            ) : null}
            <div className="file-list font-monospace flex-grow-1">
              {tab === "indexed" ? (
                indexed.length === 0 ? (
                  <p className="text-muted small px-2 py-2 mb-0">
                    No matching entries.
                  </p>
                ) : (
                  <FileTreeView paths={indexed} />
                )
              ) : ignoredPage.length === 0 ? (
                <p className="text-muted small px-2 py-2 mb-0">
                  No matching entries.
                </p>
              ) : (
                ignoredPage.map((item) => (
                  <div
                    key={item}
                    className="file-list-row text-break"
                    role="listitem"
                  >
                    {item}
                  </div>
                ))
              )}
            </div>
            {tab === "ignored" && pageCount > 1 ? (
              <div className="d-flex justify-content-between align-items-center mt-2">
                <button
                  type="button"
                  className="btn btn-sm btn-outline-secondary"
                  disabled={page === 0}
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                >
                  Previous
                </button>
                <span className="small text-muted">
                  Page {page + 1} / {pageCount}
                </span>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-secondary"
                  disabled={page >= pageCount - 1}
                  onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
                >
                  Next
                </button>
              </div>
            ) : null}
          </>
        )}
      </Offcanvas.Body>
    </Offcanvas>
  );
}
