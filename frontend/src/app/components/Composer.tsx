import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";

type ComposerProps = {
  disabled: boolean;
  busy: boolean;
  onSend: (text: string) => void;
  onStop: () => void;
};

export function Composer({ disabled, busy, onSend, onStop }: ComposerProps) {
  const [value, setValue] = useState("");
  const areaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = areaRef.current;
    if (!el) {
      return;
    }
    el.style.height = "auto";
    const next = Math.min(el.scrollHeight, 8 * 24);
    el.style.height = `${Math.max(next, 40)}px`;
  }, [value]);

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || disabled || busy) {
      return;
    }
    onSend(trimmed);
    setValue("");
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  }

  return (
    <form
      className="composer"
      onSubmit={(event: FormEvent) => {
        event.preventDefault();
        submit();
      }}
    >
      <Form.Control
        as="textarea"
        ref={areaRef}
        rows={1}
        value={value}
        disabled={disabled}
        aria-label="Message"
        placeholder={
          disabled ? "Select a completed repository to ask…" : "Ask about this repository…"
        }
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={onKeyDown}
        className="composer-input"
      />
      <div className="composer-actions">
        {busy ? (
          <Button type="button" variant="outline-secondary" size="sm" onClick={onStop}>
            Stop
          </Button>
        ) : (
          <Button type="submit" size="sm" disabled={disabled || !value.trim()}>
            Send
          </Button>
        )}
      </div>
    </form>
  );
}
