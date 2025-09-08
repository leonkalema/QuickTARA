// Centralized API base URL configuration (SvelteKit + Vite)
// Use build-time reference to import.meta.env.VITE_API_BASE_URL.
// Fallback to same-origin '/api' only in the browser.
import { browser } from '$app/environment';

export const API_BASE_URL: string =
  (import.meta.env && (import.meta.env as any).VITE_API_BASE_URL) ??
  (browser ? `${window.location.origin}/api` : '/api');
