<script lang="ts">
  import { onMount } from "svelte";
  import {
    buy,
    createAccount,
    deposit,
    fetchHoldings,
    fetchProfitLoss,
    fetchSnapshot,
    fetchTransactions,
    fetchPortfolioValue,
    generateSessionId,
    sell,
    withdraw,
  } from "./lib/api";
  import type { AccountSnapshot, Transaction } from "./lib/types";

  let sessionId = "";
  let username = "guest";
  let initialDeposit = 0;
  let amount = 100;
  let tradeSymbol = "AAPL";
  let tradeQuantity = 1;
  let status = "Set or generate a session to begin.";
  let snapshot: AccountSnapshot | null = null;
  let holdings: Record<string, number> = {};
  let transactions: Transaction[] = [];
  let loading = false;

  const setSession = () => {
    sessionId = sessionId || generateSessionId();
    status = `Using session ${sessionId}`;
  };

  const applyAccountState = (account?: AccountSnapshot | null) => {
    if (account) {
      snapshot = account;
      holdings = account.holdings || {};
      transactions = account.transactions || [];
    }
  };

  const handleCreate = async () => {
    loading = true;
    try {
      const res = await createAccount({ sessionId, username, initialDeposit });
      status = res.message;
      sessionId = res.session_id || sessionId;
      applyAccountState(res.data?.account as AccountSnapshot);
    } catch (error) {
      status = (error as Error).message;
    } finally {
      loading = false;
    }
  };

  const handleDeposit = async () => {
    if (!sessionId) {
      status = "Set a session first.";
      return;
    }
    loading = true;
    try {
      const res = await deposit(sessionId, amount);
      status = res.message;
      applyAccountState(res.data?.account as AccountSnapshot);
    } catch (error) {
      status = (error as Error).message;
    } finally {
      loading = false;
    }
  };

  const handleWithdraw = async () => {
    if (!sessionId) {
      status = "Set a session first.";
      return;
    }
    loading = true;
    try {
      const res = await withdraw(sessionId, amount);
      status = res.message;
      applyAccountState(res.data?.account as AccountSnapshot);
    } catch (error) {
      status = (error as Error).message;
    } finally {
      loading = false;
    }
  };

  const handleTrade = async (kind: "buy" | "sell") => {
    if (!sessionId) {
      status = "Set a session first.";
      return;
    }
    loading = true;
    try {
      const fn = kind === "buy" ? buy : sell;
      const res = await fn(sessionId, tradeSymbol, tradeQuantity);
      status = res.message;
      applyAccountState(res.data?.account as AccountSnapshot);
    } catch (error) {
      status = (error as Error).message;
    } finally {
      loading = false;
    }
  };

  const refresh = async () => {
    if (!sessionId) {
      status = "Set a session first.";
      return;
    }
    loading = true;
    try {
      const [snapshotRes, holdingsRes, transactionsRes, valueRes, pnlRes] = await Promise.all([
        fetchSnapshot(sessionId),
        fetchHoldings(sessionId),
        fetchTransactions(sessionId),
        fetchPortfolioValue(sessionId),
        fetchProfitLoss(sessionId),
      ]);
      sessionId = snapshotRes.session_id || sessionId;
      snapshot = snapshotRes.data?.account as AccountSnapshot;
      holdings = holdingsRes.data?.holdings || {};
      transactions = (transactionsRes.data?.transactions as Transaction[]) || [];
      if (snapshot) {
        snapshot.portfolio_value = valueRes.data?.portfolio_value ?? snapshot.portfolio_value;
        snapshot.profit_or_loss = pnlRes.data?.profit_loss ?? snapshot.profit_or_loss;
      }
      status = "Data refreshed";
    } catch (error) {
      status = (error as Error).message;
    } finally {
      loading = false;
    }
  };

  onMount(() => {
    setSession();
  });
</script>

<main class="grid">
  <section class="card">
    <h2>Session</h2>
    <label>
      Session Token
      <input bind:value={sessionId} placeholder="Provide or auto-generate" />
    </label>
    <button on:click={setSession}>Use Session</button>
    <p>{status}</p>
  </section>

  <section class="card">
    <h2>Create Account</h2>
    <label>
      Username
      <input bind:value={username} />
    </label>
    <label>
      Initial Deposit
      <input type="number" min="0" step="0.01" bind:value={initialDeposit} />
    </label>
    <button on:click={handleCreate} disabled={loading}>Create</button>
  </section>

  <section class="card">
    <h2>Cash Actions</h2>
    <label>
      Amount
      <input type="number" min="1" step="1" bind:value={amount} />
    </label>
    <div style="display: flex; gap: 8px;">
      <button on:click={handleDeposit} disabled={loading}>Deposit</button>
      <button on:click={handleWithdraw} disabled={loading}>Withdraw</button>
    </div>
  </section>

  <section class="card">
    <h2>Trading</h2>
    <label>
      Symbol
      <input bind:value={tradeSymbol} />
    </label>
    <label>
      Quantity
      <input type="number" min="1" step="1" bind:value={tradeQuantity} />
    </label>
    <div style="display: flex; gap: 8px;">
      <button on:click={() => handleTrade("buy")} disabled={loading}>Buy</button>
      <button on:click={() => handleTrade("sell")} disabled={loading}>Sell</button>
    </div>
  </section>

  <section class="card">
    <h2>Portfolio</h2>
    <button on:click={refresh} disabled={loading}>Refresh</button>
    {#if snapshot}
      <p><strong>User:</strong> {snapshot.username}</p>
      <p><strong>Balance:</strong> ${snapshot.balance?.toFixed(2)}</p>
      <p><strong>Value:</strong> ${snapshot.portfolio_value?.toFixed(2)}</p>
      <p><strong>P/L:</strong> ${snapshot.profit_or_loss?.toFixed(2)}</p>
    {:else}
      <p>No data yet.</p>
    {/if}
  </section>

  <section class="card">
    <h2>Holdings</h2>
    {#if Object.keys(holdings).length}
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Quantity</th>
          </tr>
        </thead>
        <tbody>
          {#each Object.entries(holdings) as [sym, qty]}
            <tr>
              <td>{sym}</td>
              <td>{qty}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p>No holdings yet.</p>
    {/if}
  </section>

  <section class="card" style="grid-column: 1/-1;">
    <h2>Transactions</h2>
    {#if transactions.length}
      <table>
        <thead>
          <tr>
            <th>Type</th>
            <th>Symbol</th>
            <th>Qty</th>
            <th>Price</th>
            <th>Amount</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {#each transactions as txn}
            <tr>
              <td>{txn.type}</td>
              <td>{txn.symbol || "-"}</td>
              <td>{txn.quantity ?? "-"}</td>
              <td>{txn.price ?? "-"}</td>
              <td>{txn.amount ?? "-"}</td>
              <td>{txn.timestamp}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p>No transactions yet.</p>
    {/if}
  </section>
</main>
