import { browser } from '$app/environment';
import { writable } from 'svelte/store';

const initialToken = browser ? localStorage.getItem('session_token') : null;

export const sessionToken = writable<string | null>(initialToken);

sessionToken.subscribe((value) => {
  if (!browser) {
    return;
  }
  if (value) {
    localStorage.setItem('session_token', value);
  } else {
    localStorage.removeItem('session_token');
  }
});

export const setSessionToken = (token: string) => sessionToken.set(token);
export const clearSessionToken = () => sessionToken.set(null);
