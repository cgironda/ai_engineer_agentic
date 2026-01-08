import { browser } from '$app/environment';
import { writable } from 'svelte/store';

const TOKEN_KEY = 'session_token';

const readStoredToken = () => {
  if (!browser) {
    return null;
  }
  try {
    return sessionStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
};

const initialToken = readStoredToken();

export const sessionToken = writable<string | null>(initialToken);

sessionToken.subscribe((value) => {
  if (!browser) {
    return;
  }
  try {
    if (value) {
      sessionStorage.setItem(TOKEN_KEY, value);
    } else {
      sessionStorage.removeItem(TOKEN_KEY);
    }
  } catch {
    // Ignore storage failures (private mode or blocked storage).
  }
});

export const setSessionToken = (token: string) => sessionToken.set(token);
export const clearSessionToken = () => sessionToken.set(null);
