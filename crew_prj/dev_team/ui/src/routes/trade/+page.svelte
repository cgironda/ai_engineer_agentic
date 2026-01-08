<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { setSessionActive } from '$lib/session';
  import type { AccountSummary } from '$lib/types';

  let depositAmount = 1000;
  let withdrawAmount = 500;
  let symbol = 'AAPL';
  let quantity = 10;
  let status: AccountSummary | null = null;
  let message = '';
  let error = '';
  let loading = false;

  const updateStatus = async () => {
    const response = await api.status();
    if (response.success && response.data) {
      status = response.data.account;
      setSessionActive(true);
    } else {
      setSessionActive(false);
    }
  };

  const runAction = async (action: () => Promise<{ success: boolean; message: string }>) => {
    loading = true;
    error = '';
    message = '';
    try {
      const response = await action();
      if (!response.success) {
        error = response.message;
        return;
      }
      message = response.message;
      await updateStatus();
    } catch (err) {
      error = 'Action failed. Check the API connection.';
    } finally {
      loading = false;
    }
  };

  onMount(async () => {
    await updateStatus();
  });
</script>

<section class="grid-2">
  <div class="card">
    <h2>Cash Management</h2>
    <div class="input-row">
      <label>
        Deposit Amount
        <input type="number" min="1" bind:value={depositAmount} />
      </label>
      <button class="secondary" on:click={() => runAction(() => api.deposit(Number(depositAmount)))} disabled={loading}>
        Deposit
      </button>
      <label>
        Withdraw Amount
        <input type="number" min="1" bind:value={withdrawAmount} />
      </label>
      <button on:click={() => runAction(() => api.withdraw(Number(withdrawAmount)))} disabled={loading}>
        Withdraw
      </button>
    </div>
  </div>

  <div class="card">
    <h2>Execute Trade</h2>
    <div class="input-row">
      <label>
        Symbol
        <input type="text" bind:value={symbol} />
      </label>
      <label>
        Quantity
        <input type="number" min="1" bind:value={quantity} />
      </label>
      <button class="secondary" on:click={() => runAction(() => api.buy(symbol, Number(quantity)))} disabled={loading}>
        Buy Shares
      </button>
      <button on:click={() => runAction(() => api.sell(symbol, Number(quantity)))} disabled={loading}>
        Sell Shares
      </button>
    </div>
  </div>
</section>

<section class="card">
  <h2>Account Status</h2>
  {#if status}
    <div class="status-grid">
      <div class="status-tile">
        <span>Cash Balance</span>
        <strong>${status.balance.toFixed(2)}</strong>
      </div>
      <div class="status-tile">
        <span>Portfolio Value</span>
        <strong>${status.portfolio_value.toFixed(2)}</strong>
      </div>
      <div class="status-tile">
        <span>Profit / Loss</span>
        <strong>${status.profit_loss.toFixed(2)}</strong>
      </div>
    </div>
  {:else}
    <p class="muted">Run a trade to see updated balances.</p>
  {/if}
  {#if message}
    <p class="notice success">{message}</p>
  {/if}
  {#if error}
    <p class="notice">{error}</p>
  {/if}
</section>
