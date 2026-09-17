import { useState, type ChangeEvent, type FormEvent } from "react";
import Alert from "react-bootstrap/Alert";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import Modal from "react-bootstrap/Modal";
import Spinner from "react-bootstrap/Spinner";

import { ingestZip } from "../api";
import type { Repository } from "../types";

type IngestModalProps = {
  show: boolean;
  onHide: () => void;
  onSuccess: (repository: Repository) => void;
};

export function IngestModal({ show, onHide, onSuccess }: IngestModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [ingestError, setIngestError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function resetLocal() {
    setFile(null);
    setFileError(null);
    setIngestError(null);
    setBusy(false);
  }

  function handleHide() {
    if (busy) {
      return;
    }
    resetLocal();
    onHide();
  }

  function onFileChange(next: File | null) {
    setFileError(null);
    setIngestError(null);
    if (next && !next.name.toLowerCase().endsWith(".zip")) {
      setFile(null);
      setFileError("Choose a .zip file");
      return;
    }
    setFile(next);
  }

  async function runIngest() {
    if (!file) {
      setFileError("Choose a .zip file");
      return;
    }
    setBusy(true);
    setIngestError(null);
    try {
      const repository = await ingestZip(file);
      resetLocal();
      onSuccess(repository);
    } catch (error) {
      setIngestError(error instanceof Error ? error.message : "Ingest failed");
      setBusy(false);
    }
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    await runIngest();
  }

  return (
    <Modal show={show} onHide={handleHide} centered aria-labelledby="ingest-modal-title">
      <Modal.Header closeButton={!busy}>
        <Modal.Title as="h2" id="ingest-modal-title" className="h5 mb-0">
          New repository
        </Modal.Title>
      </Modal.Header>
      <Form onSubmit={(event) => void onSubmit(event)}>
        <Modal.Body>
          <p className="text-muted small">
            Upload a source ZIP. Re-uploading the same repository name replaces
            the previous index. Reviewer sample:{" "}
            <code>sample-data/fixture-repository/</code>
          </p>
          <Form.Group controlId="zip-file">
            <Form.Label>Repository ZIP</Form.Label>
            <Form.Control
              type="file"
              accept=".zip,application/zip"
              disabled={busy}
              onChange={(event: ChangeEvent<HTMLInputElement>) =>
                onFileChange(event.currentTarget.files?.item(0) ?? null)
              }
            />
            {file ? (
              <Form.Text className="text-muted">Selected: {file.name}</Form.Text>
            ) : null}
          </Form.Group>
          {fileError ? (
            <Alert variant="warning" className="mt-3 mb-0" role="alert">
              {fileError}
            </Alert>
          ) : null}
          {ingestError ? (
            <Alert variant="danger" className="mt-3 mb-0" role="alert">
              {ingestError}{" "}
              <Button
                type="button"
                size="sm"
                variant="outline-danger"
                onClick={() => void runIngest()}
              >
                Retry
              </Button>
            </Alert>
          ) : null}
          {busy ? (
            <div className="d-flex align-items-center gap-2 mt-3" role="status" aria-live="polite">
              <Spinner animation="border" size="sm" />
              <span>Indexing repository…</span>
            </div>
          ) : null}
        </Modal.Body>
        <Modal.Footer>
          <Button type="button" variant="outline-secondary" onClick={handleHide} disabled={busy}>
            Cancel
          </Button>
          <Button type="submit" disabled={busy || !file}>
            Ingest
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
