const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();

export const API_URL = configuredApiUrl || (
  import.meta.env.DEV ? 'http://localhost:8000' : ''
);

export function requireApiUrl() {
  if (!API_URL) {
    throw new Error('The backend API URL is not configured. Set VITE_API_URL for the deployed frontend.');
  }
  return API_URL;
}
