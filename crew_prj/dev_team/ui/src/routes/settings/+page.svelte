<script lang="ts">
  import { api } from '$lib/api';
  import { sessionActive, setSessionActive } from '$lib/session';

  let tokenInput = '';
  let message = '';
  let error = '';

  const restoreSession = async () => {
    message = '';
    error = '';
    const trimmed = tokenInput.trim();
    if (!trimmed) {
      error = 'Enter a session token to restore.';
      return;
    }
    const response = await api.setSession(trimmed);
    if (!response.success) {
      error = response.message;
      setSessionActive(false);
      return;
    }
    setSessionActive(true);
    message = response.message;
  };

  const clearSession = async () => {
    message = '';
    error = '';
    await api.logout();
    setSessionActive(false);
    message = 'Session cleared.';
  };
</script>

<section class="grid-2">
  <div class="card">
    <h2>Session Control</h2>
    <p class="muted">Restore a session token if you have one, or clear the active session.</p>
    <div class="input-row">
      <label>
        Session Token
        <input type="text" bind:value={tokenInput} placeholder="Paste token" />
      </label>
      <button class="secondary" on:click={restoreSession}>Restore Session</button>
      <button class="ghost" on:click={clearSession} disabled={!$sessionActive}>Clear</button>
    </div>
    {#if message}
      <p class="notice success">{message}</p>
    {/if}
    {#if error}
      <p class="notice">{error}</p>
    {/if}
  </div>

  <div class="card">
    <h2>API Endpoint</h2>
    <p class="muted">Configure the backend URL via <code>VITE_API_BASE_URL</code>.</p>
    <p class="tag">Default: http://localhost:8000</p>
    <p class="muted">If you changed ports, update the env file and restart the UI.</p>
  </div>
</section>
