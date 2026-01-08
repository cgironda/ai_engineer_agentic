<script lang="ts">
  import { sessionToken, setSessionToken, clearSessionToken } from '$lib/session';

  let tokenInput = '';

  const saveToken = () => {
    if (tokenInput.trim()) {
      setSessionToken(tokenInput.trim());
    }
  };
</script>

<section class="grid-2">
  <div class="card">
    <h2>Session Control</h2>
    <p class="muted">Paste a session token to resume work across devices.</p>
    <div class="input-row">
      <label>
        Session Token
        <input type="text" bind:value={tokenInput} placeholder={$sessionToken ?? 'Paste token'} />
      </label>
      <button class="secondary" on:click={saveToken}>Save Token</button>
      <button class="ghost" on:click={clearSessionToken}>Clear</button>
    </div>
  </div>

  <div class="card">
    <h2>API Endpoint</h2>
    <p class="muted">Configure the backend URL via <code>VITE_API_BASE_URL</code>.</p>
    <p class="tag">Default: http://localhost:8000</p>
    <p class="muted">If you changed ports, update the env file and restart the UI.</p>
  </div>
</section>
