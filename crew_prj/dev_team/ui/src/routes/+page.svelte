<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { setSessionActive } from '$lib/session';
  import PortfolioChart from '$lib/PortfolioChart.svelte';
  import type { AccountSummary, HoldingSnapshot, PricesData } from '$lib/types';

  let username = 'Trader1';
  let initialDeposit = 10000;
  let status: AccountSummary | null = null;
  let holdings: HoldingSnapshot | null = null;
  let prices: PricesData | null = null;
  let message = '';
  let error = '';
  let loading = false;

  const refresh = async () => {
    loading = true;
    error = '';
    try {
      const [statusResponse, holdingsResponse, pricesResponse] = await Promise.all([
        api.status(),
        api.holdings(),
        api.prices()
      ]);
      if (!statusResponse.success) {
        error = statusResponse.message;
        setSessionActive(false);
      } else {
        status = statusResponse.data?.account ?? null;
        setSessionActive(true);
      }
      if (holdingsResponse.success) {
        holdings = holdingsResponse.data ?? null;
      }
      if (pricesResponse.success) {
        prices = pricesResponse.data ?? null;
      }
    } catch (err) {
      error = 'Unable to refresh account data.';
    } finally {
      loading = false;
    }
  };

  const handleCreate = async () => {
    loading = true;
    error = '';
    message = '';
    try {
      const response = await api.createAccount(username, Number(initialDeposit));
      if (!response.success) {
        error = response.message;
        return;
      }
      const data = response.data;
      if (data) {
        status = data.account;
        holdings = data.holdings;
        message = response.message;
        setSessionActive(true);
      }
    } catch (err) {
      error = 'Unable to create account.';
    } finally {
      loading = false;
    }
  };

  onMount(async () => {
    await refresh();
  });
</script>

<section class="grid-2">
  <div class="card">
    <h2>Account Snapshot</h2>
    <p class="muted">Create a session or refresh your latest portfolio state.</p>
    <div class="input-row">
      <label>
        Username
        <input type="text" bind:value={username} />
      </label>
      <label>
        Initial Deposit
        <input type="number" min="1" bind:value={initialDeposit} />
      </label>
      <button on:click={handleCreate} disabled={loading}>Create Account</button>
      <button class="secondary" on:click={refresh} disabled={loading}>Refresh</button>
    </div>
    {#if message}
      <p class="notice success">{message}</p>
    {/if}
    {#if error}
      <p class="notice">{error}</p>
    {/if}
  </div>

  <div class="card">
    <h2>Portfolio Momentum</h2>
    <p class="muted">Lightweight trend view for the last few valuation points.</p>
    <PortfolioChart values={[10, 16, 12, 22, 18, 28, 24]} />
    <span class="tag">Signal: steady climb</span>
  </div>
</section>

<section class="card">
  <h2>Balances</h2>
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
    <p class="muted">No account session loaded yet.</p>
  {/if}
</section>

<section class="grid-2">
  <div class="card">
    <h2>Holdings</h2>
    {#if holdings && Object.keys(holdings.holdings).length > 0}
      <table class="table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Shares</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {#each Object.entries(holdings.holdings) as [symbol, quantity]}
            <tr>
              <td>{symbol}</td>
              <td>{quantity}</td>
              <td>${(holdings.holding_values[symbol] ?? 0).toFixed(2)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p class="muted">No holdings yet.</p>
    {/if}
  </div>

  <div class="card">
    <h2>Market Prices</h2>
    {#if prices}
      <table class="table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Price</th>
          </tr>
        </thead>
        <tbody>
          {#each Object.entries(prices.symbols) as [symbol, price]}
            <tr>
              <td>{symbol}</td>
              <td>${price.toFixed(2)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p class="muted">Prices will appear after refresh.</p>
    {/if}
  </div>
</section>
