import { useEffect, useState, type ReactNode } from "react";
import Offcanvas from "react-bootstrap/Offcanvas";

type AppShellProps = {
  sidebar: ReactNode;
  sidebarOpen: boolean;
  onSidebarHide: () => void;
  topBar: ReactNode;
  main: ReactNode;
  files?: ReactNode;
};

const LG_UP = "(min-width: 992px)";

function useLgUp(): boolean {
  const [lgUp, setLgUp] = useState(() => {
    if (typeof window === "undefined" || !window.matchMedia) {
      return true;
    }
    return window.matchMedia(LG_UP).matches;
  });

  useEffect(() => {
    const media = window.matchMedia(LG_UP);
    const onChange = () => setLgUp(media.matches);
    onChange();
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  return lgUp;
}

export function AppShell({
  sidebar,
  sidebarOpen,
  onSidebarHide,
  topBar,
  main,
  files,
}: AppShellProps) {
  const lgUp = useLgUp();

  return (
    <div className="app-root" data-bs-theme-root>
      {lgUp ? (
        <aside className="app-sidebar d-flex flex-column">{sidebar}</aside>
      ) : (
        <Offcanvas
          show={sidebarOpen}
          onHide={onSidebarHide}
          placement="start"
          className="app-offcanvas-sidebar"
          aria-labelledby="repo-sidebar-label"
        >
          <Offcanvas.Header closeButton>
            <Offcanvas.Title id="repo-sidebar-label" as="h2" className="h6 mb-0">
              Repositories
            </Offcanvas.Title>
          </Offcanvas.Header>
          <Offcanvas.Body className="p-0 d-flex flex-column">{sidebar}</Offcanvas.Body>
        </Offcanvas>
      )}

      <div className="app-main d-flex flex-column">
        <header className="app-topbar">{topBar}</header>
        <div className="app-main-body flex-grow-1 min-h-0">{main}</div>
      </div>

      {lgUp && files ? (
        <aside className="app-files d-flex flex-column">{files}</aside>
      ) : null}
    </div>
  );
}
