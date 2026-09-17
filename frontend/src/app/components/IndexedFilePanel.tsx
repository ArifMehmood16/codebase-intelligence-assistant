import { useMemo, useState } from "react";
import Form from "react-bootstrap/Form";

import type { Repository } from "../types";
import { FileTreeView } from "./FileTree";

type IndexedFilePanelProps = {
  repository: Repository | null;
};

export function IndexedFilePanel({ repository }: IndexedFilePanelProps) {
  const [filter, setFilter] = useState("");
  const paths = useMemo(() => {
    const all = repository?.indexedPaths ?? [];
    const query = filter.trim().toLowerCase();
    if (!query) {
      return all;
    }
    return all.filter((path) => path.toLowerCase().includes(query));
  }, [repository, filter]);

  return (
    <section className="file-panel" aria-labelledby="indexed-files-heading">
      <header className="file-panel-header">
        <h2 id="indexed-files-heading" className="h6 mb-0">
          Indexed files
        </h2>
        {repository ? (
          <p className="text-muted small mb-0">
            {repository.indexedFileCount} file
            {repository.indexedFileCount === 1 ? "" : "s"}
          </p>
        ) : null}
      </header>
      {!repository ? (
        <p className="text-muted small px-3 py-3 mb-0">
          Select a repository to see indexed files.
        </p>
      ) : (
        <>
          <div className="file-panel-filter">
            <Form.Control
              type="search"
              size="sm"
              placeholder="Filter files…"
              value={filter}
              aria-label="Filter indexed files"
              onChange={(event) => setFilter(event.target.value)}
            />
          </div>
          <div className="file-panel-body">
            <FileTreeView paths={paths} />
          </div>
        </>
      )}
    </section>
  );
}
