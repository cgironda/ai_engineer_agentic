import {
  type AccountData,
  type ApiResponse,
  type CreateAccountData,
  type HoldingsData,
  type PricesData,
  type TransactionsData,
  type TradeSnapshot
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

async function request<T>(path: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers ?? {})
  };

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include'
  });

  return (await response.json()) as ApiResponse<T>;
}

export const api = {
  createAccount: (username: string, initialDeposit: number) =>
    request<CreateAccountData>('/api/account', {
      method: 'POST',
      body: JSON.stringify({ username, initial_deposit: initialDeposit })
    }),
  deposit: (amount: number) =>
    request<AccountData>('/api/deposit', {
      method: 'POST',
      body: JSON.stringify({ amount })
    }),
  withdraw: (amount: number) =>
    request<AccountData>('/api/withdraw', {
      method: 'POST',
      body: JSON.stringify({ amount })
    }),
  buy: (symbol: string, quantity: number) =>
    request<{ trade: TradeSnapshot } & HoldingsData>('/api/trade/buy', {
      method: 'POST',
      body: JSON.stringify({ symbol, quantity })
    }),
  sell: (symbol: string, quantity: number) =>
    request<{ trade: TradeSnapshot } & HoldingsData>('/api/trade/sell', {
      method: 'POST',
      body: JSON.stringify({ symbol, quantity })
    }),
  status: () => request<AccountData>('/api/status'),
  holdings: () => request<HoldingsData>('/api/holdings'),
  transactions: () => request<TransactionsData>('/api/transactions'),
  prices: () => request<PricesData>('/api/prices'),
  setSession: (token: string) =>
    request<AccountData>('/api/session', {
      method: 'POST',
      body: JSON.stringify({ token })
    }),
  logout: () =>
    request<{}>('/api/logout', {
      method: 'POST'
    })
};
