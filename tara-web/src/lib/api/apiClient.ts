import { browser } from '$app/environment';
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';
import { API_BASE_URL } from '$lib/config';
import { notifications } from '$lib/stores/notificationStore';
import { goto } from '$app/navigation';

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export function getAuthHeaders(): HeadersInit {
  const auth = get(authStore);
  const tokenFromStorage: string | null = browser ? localStorage.getItem('auth_token') : null;
  const token: string | null = auth.token ?? tokenFromStorage;
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

export async function handleResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    authStore.logout();
    notifications.show('Your session has expired. Please sign in again.', 'error');
    if (browser) goto('/auth');
    throw new ApiError('Session expired', 401, '');
  }
  if (!response.ok) {
    const body = await response.text();
    let userMessage: string;
    try {
      const parsed = JSON.parse(body);
      userMessage = parsed.detail ?? parsed.message ?? body;
    } catch {
      userMessage = body;
    }
    throw new ApiError(userMessage, response.status, body);
  }
  return response.json() as Promise<T>;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { ...getAuthHeaders(), ...(options.headers ?? {}) }
  });
  return handleResponse<T>(response);
}
