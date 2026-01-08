<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { setSessionActive } from '$lib/session';

  let transactions: string[] = [];
  let message = '';
  let error = '';
  let loading = false;

  const refresh = async () => {
    loading = true;
    error = '';
    try {
      const response = await api.transactions();
      if (!response.success) {
        error = response.message;
        setSessionActive(false);
        return;
      }
      transactions = response.data?.transactions ?? [];
      message = response.message;
      setSessionActive(true);
    } catch (err) {
      error = 'Unable to load transactions.';
    } finally {
      loading = false;
    }
  };

  onMount(async () => {
    await refresh();
  });
</script>

<section class="card">
  <h2>Transaction History</h2>
  <p class="muted">Every cash movement and trade activity in the session.</p>
  <button class="secondary" on:click={refresh} disabled={loading}>Refresh</button>
  {#if message}
    <p class="notice success">{message}</p>
  {/if}
  {#if error}
    <p class="notice">{error}</p>
  {/if}
  {#if transactions.length}
    <table class="table">
      <thead>
        <tr>
          <th>#</th>
          <th>Event</th>
        </tr>
      </thead>
      <tbody>
        {#each transactions as transaction, index}
          <tr>
            <td>{index + 1}</td>
            <td>{transaction}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else}
    <p class="muted">No transactions recorded yet.</p>
  {/if}
</section>
