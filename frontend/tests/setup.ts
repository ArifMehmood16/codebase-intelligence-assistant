import { cleanup } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import { afterEach, beforeAll } from "vitest";

beforeAll(() => {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: (query: string) => ({
      // Desktop layout in unit tests (aside sidebar, not offcanvas).
      matches: query.includes("min-width: 992px"),
      media: query,
      onchange: null,
      addListener: () => undefined,
      removeListener: () => undefined,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
      dispatchEvent: () => false,
    }),
  });

  if (typeof crypto.randomUUID !== "function") {
    Object.defineProperty(crypto, "randomUUID", {
      value: () => "00000000-0000-4000-8000-000000000001",
    });
  }
});

afterEach(() => {
  cleanup();
  sessionStorage.clear();
});
