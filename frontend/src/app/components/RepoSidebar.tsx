import Button from "react-bootstrap/Button";

import type { Repository } from "../types";
import { RepoListItem } from "./RepoListItem";

type RepoSidebarProps = {
  repositories: Repository[];
  selectedId: string | null;
  seenAtById: Record<string, number>;
  busy: boolean;
  listError: string | null;
  onRetryList: () => void;
  onSelect: (repositoryId: string) => void;
  onNewRepository: () => void;
};

export function RepoSidebar({
  repositories,
  selectedId,
  seenAtById,
  busy,
  listError,
  onRetryList,
  onSelect,
  onNewRepository,
}: RepoSidebarProps) {
  return (
    <>
      <div className="sidebar-brand px-3 py-3 border-bottom">
        <div className="sidebar-product-name">Codebase Assistant</div>
        <div className="text-muted small">Local repository Q&amp;A</div>
      </div>
      <div className="px-3 py-2 border-bottom">
        <Button
          type="button"
          className="w-100"
          variant="primary"
          size="sm"
          onClick={onNewRepository}
          disabled={busy}
        >
          New repository
        </Button>
      </div>
      {listError ? (
        <div className="px-3 py-2" role="alert">
          <div className="small text-danger mb-2">{listError}</div>
          <Button type="button" size="sm" variant="outline-secondary" onClick={onRetryList}>
            Retry
          </Button>
        </div>
      ) : null}
      <div className="repo-scroll flex-grow-1" aria-label="Indexed repositories">
        {repositories.length === 0 ? (
          <p className="text-muted small px-3 py-3 mb-0">
            No repositories yet. Add a ZIP to begin.
          </p>
        ) : (
          repositories.map((repo) => (
            <RepoListItem
              key={repo.repositoryId}
              repository={repo}
              selected={selectedId === repo.repositoryId}
              seenAt={seenAtById[repo.repositoryId] ?? Date.now()}
              disabled={busy}
              onSelect={onSelect}
            />
          ))
        )}
      </div>
    </>
  );
}
