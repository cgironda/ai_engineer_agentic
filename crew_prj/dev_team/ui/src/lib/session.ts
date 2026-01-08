import { writable } from 'svelte/store';

export const sessionActive = writable(false);

export const setSessionActive = (active: boolean) => sessionActive.set(active);
