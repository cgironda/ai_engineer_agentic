<script lang="ts">
  import '../app.css';
  import { api } from '$lib/api';
  import { sessionActive, setSessionActive } from '$lib/session';

  const handleLogout = async () => {
    await api.logout();
    setSessionActive(false);
  };
</script>

<svelte:head>
  <title>AI Trading Console</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Newsreader:wght@400;600&family=Space+Grotesk:wght@400;600;700&display=swap"
    rel="stylesheet"
  />
</svelte:head>

<div class="app-shell">
  <header class="header">
    <div class="brand">
      <div class="logo"></div>
      <div>
        <h1>AI Trading Console</h1>
        <p class="muted">Gradio-backed actions with a Svelte command center.</p>
      </div>
    </div>
    <nav class="nav">
      <a href="/">Dashboard</a>
      <a href="/trade">Trade</a>
      <a href="/transactions">Transactions</a>
      <a href="/settings">Settings</a>
      {#if $sessionActive}
        <button class="ghost" on:click={handleLogout}>Clear Session</button>
      {/if}
    </nav>
  </header>

  <main class="main">
    <slot />
  </main>
</div>
