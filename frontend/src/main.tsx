import "bootstrap/dist/css/bootstrap.min.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./app/App";

function applyColorScheme(): void {
  const dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  document.documentElement.setAttribute(
    "data-bs-theme",
    dark ? "dark" : "light",
  );
}

applyColorScheme();
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", applyColorScheme);

const rootElement = document.getElementById("root");
if (rootElement === null) {
  throw new Error("Root element #root is missing");
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
