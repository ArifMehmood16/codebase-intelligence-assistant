import { useCallback, useEffect, useMemo, useState } from "react";
import Button from "react-bootstrap/Button";
import Dropdown from "react-bootstrap/Dropdown";

import { deleteRepository, getRepository, listRepositories } from "./api";
import "./App.css";
import { AppShell } from "./components/AppShell";
import { ChatThread } from "./components/ChatThread";
import { FileDrawer } from "./components/FileDrawer";
import { IndexedFilePanel } from "./components/IndexedFilePanel";
import { IngestModal } from "./components/IngestModal";
import { RepoSidebar } from "./components/RepoSidebar";
import { rememberRepoSeen } from "./sessionPrefs";
import type { Repository } from "./types";
import { repositoryDisplayName, repositoryNameKey } from "./types";
import { useChat } from "./useChat";

export { repositoryDisplayName } from "./types";

export function App() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [seenAtById, setSeenAtById] = useState<Record<string, number>>({});
  const [listError, setListError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [ingestOpen, setIngestOpen] = useState(false);
  const [filesOpen, setFilesOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const selected = useMemo(
    () => repositories.find((repo) => repo.repositoryId === selectedId) ?? null,
    [repositories, selectedId],
  );

  const chat = useChat(selected);

  const refreshRepositories = useCallback(async () => {
    setListError(null);
    try {
      const listed = await listRepositories();
      const seen: Record<string, number> = {};
      for (const repo of listed) {
        seen[repo.repositoryId] = rememberRepoSeen(repo.repositoryId);
      }
      setSeenAtById(seen);
      setRepositories(listed);
      setSelectedId((current) => {
        if (current && listed.some((repo) => repo.repositoryId === current)) {
          return current;
        }
        return listed[0]?.repositoryId ?? null;
      });
    } catch (error) {
      setListError(
        error instanceof Error ? error.message : "Could not load repositories",
      );
    }
  }, []);

  useEffect(() => {
    void refreshRepositories();
  }, [refreshRepositories]);

  async function onSelect(repositoryId: string) {
    setSidebarOpen(false);
    setSelectedId(repositoryId);
    try {
      const fresh = await getRepository(repositoryId);
      setRepositories((prev) =>
        prev.map((repo) =>
          repo.repositoryId === repositoryId ? fresh : repo,
        ),
      );
    } catch {
      /* keep list summary */
    }
  }

  function onIngestSuccess(repository: Repository) {
    const incomingKey = repositoryNameKey(repository);
    for (const prior of repositories) {
      if (
        prior.repositoryId !== repository.repositoryId &&
        incomingKey !== null &&
        repositoryNameKey(prior) === incomingKey
      ) {
        chat.clearThreadFor(prior.repositoryId);
      }
    }
    rememberRepoSeen(repository.repositoryId);
    setIngestOpen(false);
    setDeleteError(null);
    setRepositories((prev) => {
      const withoutSameName = prev.filter((repo) => {
        if (repo.repositoryId === repository.repositoryId) {
          return false;
        }
        if (incomingKey === null) {
          return true;
        }
        return repositoryNameKey(repo) !== incomingKey;
      });
      return [repository, ...withoutSameName];
    });
    setSelectedId(repository.repositoryId);
    setSeenAtById((prev) => ({
      ...prev,
      [repository.repositoryId]: Date.now(),
    }));
    void refreshRepositories();
  }

  async function onDelete() {
    if (!selected || deleting) {
      return;
    }
    setDeleting(true);
    setDeleteError(null);
    const repositoryId = selected.repositoryId;
    try {
      await deleteRepository(repositoryId);
      chat.clearThreadFor(repositoryId);
      setFilesOpen(false);
      setSelectedId(null);
      await refreshRepositories();
    } catch (error) {
      setDeleteError(
        error instanceof Error ? error.message : "Could not delete repository",
      );
    } finally {
      setDeleting(false);
    }
  }

  const topBar = (
    <div className="topbar-inner">
      <div className="d-flex align-items-center gap-2 min-w-0">
        <Button
          type="button"
          variant="outline-secondary"
          size="sm"
          className="d-lg-none"
          aria-label="Open repositories"
          onClick={() => setSidebarOpen(true)}
        >
          Repos
        </Button>
        {selected ? (
          <Button
            type="button"
            variant="outline-secondary"
            size="sm"
            className="d-lg-none"
            aria-label="Open indexed files"
            onClick={() => setFilesOpen(true)}
          >
            Files
          </Button>
        ) : null}
        <div className="min-w-0">
          <div className="topbar-title text-truncate">
            {selected ? repositoryDisplayName(selected) : "No repository"}
          </div>
          {selected ? (
            <div className="topbar-subtitle text-muted">
              {selected.indexedFileCount} indexed · {selected.ignoredFileCount}{" "}
              ignored
            </div>
          ) : null}
        </div>
      </div>
      {selected ? (
        <div className="topbar-actions">
          <Button
            type="button"
            variant="outline-danger"
            size="sm"
            aria-label="Delete repository"
            disabled={deleting || chat.isAsking}
            onClick={() => void onDelete()}
          >
            {deleting ? "Deleting…" : "Delete"}
          </Button>
          <Dropdown align="end">
            <Dropdown.Toggle
              variant="outline-secondary"
              size="sm"
              id="repo-menu"
              className="kebab-toggle"
              aria-label="Repository actions"
              disabled={deleting || chat.isAsking}
            >
              ⋮
            </Dropdown.Toggle>
            <Dropdown.Menu>
              <Dropdown.Item as="button" type="button" onClick={() => setIngestOpen(true)}>
                Re-index
              </Dropdown.Item>
              <Dropdown.Item as="button" type="button" onClick={() => setFilesOpen(true)}>
                View indexed files
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </div>
      ) : null}
    </div>
  );

  return (
    <>
      <AppShell
        sidebarOpen={sidebarOpen}
        onSidebarHide={() => setSidebarOpen(false)}
        sidebar={
          <RepoSidebar
            repositories={repositories}
            selectedId={selectedId}
            seenAtById={seenAtById}
            busy={chat.isAsking || deleting}
            listError={listError}
            onRetryList={() => void refreshRepositories()}
            onSelect={(id) => void onSelect(id)}
            onNewRepository={() => {
              setSidebarOpen(false);
              setIngestOpen(true);
            }}
          />
        }
        topBar={topBar}
        files={<IndexedFilePanel repository={selected} />}
        main={
          <div className="d-flex flex-column h-100 min-h-0">
            {deleteError ? (
              <div className="px-3 py-2 border-bottom" role="alert">
                <span className="text-danger small me-2">{deleteError}</span>
                <Button
                  type="button"
                  size="sm"
                  variant="outline-secondary"
                  onClick={() => void onDelete()}
                >
                  Retry
                </Button>
              </div>
            ) : null}
            <div className="flex-grow-1 min-h-0">
              <ChatThread
                repository={selected}
                messages={chat.messages}
                isAsking={chat.isAsking}
                askError={chat.askError}
                onSend={(text) => void chat.send(text)}
                onRetry={(id) => void chat.retry(id)}
                onStop={chat.stop}
                onClearError={chat.clearError}
                onOpenIngest={() => setIngestOpen(true)}
              />
            </div>
          </div>
        }
      />
      <IngestModal
        show={ingestOpen}
        onHide={() => setIngestOpen(false)}
        onSuccess={onIngestSuccess}
      />
      <FileDrawer
        show={filesOpen}
        onHide={() => setFilesOpen(false)}
        repository={selected}
      />
    </>
  );
}
