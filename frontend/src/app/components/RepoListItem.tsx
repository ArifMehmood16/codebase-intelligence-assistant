import Badge from "react-bootstrap/Badge";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";

import type { Repository } from "../types";
import {
  relativeTime,
  repositoryDisplayName,
  shortHash,
} from "../types";

type RepoListItemProps = {
  repository: Repository;
  selected: boolean;
  seenAt: number;
  disabled?: boolean;
  onSelect: (repositoryId: string) => void;
};

export function RepoListItem({
  repository,
  selected,
  seenAt,
  disabled,
  onSelect,
}: RepoListItemProps) {
  const name = repositoryDisplayName(repository);
  const status = repository.status;
  const showBadge = status === "failed" || status === "indexing";
  const dotClass =
    status === "completed"
      ? "status-dot status-dot-ok"
      : status === "failed"
        ? "status-dot status-dot-bad"
        : "status-dot status-dot-warn";

  return (
    <button
      type="button"
      className={`repo-list-item ${selected ? "is-selected" : ""}`}
      disabled={disabled}
      onClick={() => onSelect(repository.repositoryId)}
      aria-current={selected ? "true" : undefined}
    >
      <div className="d-flex align-items-start gap-2">
        <OverlayTrigger
          placement="right"
          delay={{ show: 400, hide: 0 }}
          overlay={<Tooltip id={`status-${repository.repositoryId}`}>{status}</Tooltip>}
        >
          <span className={dotClass} aria-label={`Status ${status}`} />
        </OverlayTrigger>
        <div className="min-w-0 flex-grow-1">
          <div className="repo-list-name text-truncate" title={name}>
            {name}
          </div>
          <div className="repo-list-meta text-truncate">
            <span className="font-monospace">{shortHash(repository.repositoryId)}</span>
            <span aria-hidden> · </span>
            <span>{relativeTime(seenAt)}</span>
            <span aria-hidden> · </span>
            <span>
              {repository.indexedFileCount} file
              {repository.indexedFileCount === 1 ? "" : "s"}
            </span>
          </div>
          {showBadge ? (
            <Badge
              bg={status === "failed" ? "danger" : "warning"}
              text={status === "indexing" ? "dark" : undefined}
              className="mt-1"
            >
              {status}
            </Badge>
          ) : null}
        </div>
      </div>
    </button>
  );
}
