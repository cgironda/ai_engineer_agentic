import { get } from 'svelte/store';
import {
  type AccountData,
  type ApiResponse,
  type CreateAccountData,
  type HoldingsData,
  type PricesData,
  type TransactionsData,
  type TradeSnapshot
} from './types';
import { sessionToken } from './session';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const withToken = () => {
  const token = get(sessionToken);
  return token ? { 'X-Session-Token': token } : {};
};

async function request<T>(path: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  const headers = {
    'Content-Type': 'application/json',
    ...withToken(),
    ...(options.headers ?? {})
  };

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
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
  prices: () => request<PricesData>('/api/prices')
};
