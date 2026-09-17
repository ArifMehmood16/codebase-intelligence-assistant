export type FrontendConfig = {
  apiBaseUrl: string;
};

const DEFAULT_API_BASE_URL = "http://localhost:8000";

export function loadFrontendConfig(
  env: { VITE_API_BASE_URL?: string } = import.meta.env,
): FrontendConfig {
  const configured = env.VITE_API_BASE_URL?.trim();
  return { apiBaseUrl: configured || DEFAULT_API_BASE_URL };
}
