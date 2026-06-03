// Centralized API base URL configuration (SvelteKit + Vite)
// Reads the build-time VITE_API_BASE_URL, but treats unset/empty values —
// including the literal strings "undefined"/"null" that Vite can embed when
// the var is missing — as "not configured", falling back to same-origin /api.
import { browser } from '$app/environment';

const RAW_API_BASE_URL: unknown = import.meta.env?.VITE_API_BASE_URL;

function resolveConfiguredBaseUrl(raw: unknown): string | null {
  if (typeof raw !== 'string') {
    return null;
  }
  const trimmed = raw.trim();
  if (trimmed === '' || trimmed === 'undefined' || trimmed === 'null') {
    return null;
  }
  return trimmed.replace(/\/+$/, '');
}

function sameOriginFallback(): string {
  return browser ? `${window.location.origin}/api` : '/api';
}

export const API_BASE_URL: string =
  resolveConfiguredBaseUrl(RAW_API_BASE_URL) ?? sameOriginFallback();
