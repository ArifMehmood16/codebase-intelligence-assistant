import { describe, expect, it } from "vitest";

import { loadFrontendConfig } from "../../src/app/config";

describe("frontend config", () => {
  it("reads the API base URL from Vite env", () => {
    expect(
      loadFrontendConfig({ VITE_API_BASE_URL: "http://example.test:8000" })
        .apiBaseUrl,
    ).toBe("http://example.test:8000");
  });

  it("defaults the API base URL when unset", () => {
    expect(loadFrontendConfig({}).apiBaseUrl).toBe("http://localhost:8000");
  });
});
