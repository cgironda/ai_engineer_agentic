import type { AccountSnapshot, ApiResponse, Transaction } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:7860";
const SESSION_HEADER = import.meta.env.VITE_SESSION_HEADER || "X-Session-Id";

async function request<T>(
  path: string,
  options: RequestInit = {},
  sessionId?: string,
): Promise<ApiResponse<T>> {
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (sessionId) {
    headers.set(SESSION_HEADER, sessionId);
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const payload = (await res.json()) as ApiResponse<T>;
  if (!res.ok) {
    throw new Error(payload.error || payload.message || "Request failed");
  }
  return payload;
}

export function generateSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return Math.random().toString(16).slice(2);
}

export async function createAccount({
  sessionId,
  username,
  initialDeposit,
}: {
  sessionId?: string;
  username: string;
  initialDeposit: number;
}) {
  return request<{ account: AccountSnapshot }>("/api/account/create", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, username, initial_deposit: initialDeposit }),
  });
}

export async function deposit(sessionId: string, amount: number) {
  return request<{ account: AccountSnapshot }>("/api/account/deposit", {
    method: "POST",
    body: JSON.stringify({ amount }),
  }, sessionId);
}

export async function withdraw(sessionId: string, amount: number) {
  return request<{ account: AccountSnapshot }>("/api/account/withdraw", {
    method: "POST",
    body: JSON.stringify({ amount }),
  }, sessionId);
}

export async function buy(sessionId: string, symbol: string, quantity: number) {
  return request<{ account: AccountSnapshot }>("/api/trade/buy", {
    method: "POST",
    body: JSON.stringify({ symbol, quantity }),
  }, sessionId);
}

export async function sell(sessionId: string, symbol: string, quantity: number) {
  return request<{ account: AccountSnapshot }>("/api/trade/sell", {
    method: "POST",
    body: JSON.stringify({ symbol, quantity }),
  }, sessionId);
}

export async function fetchSnapshot(sessionId: string) {
  return request<{ account: AccountSnapshot }>("/api/account/snapshot", {}, sessionId);
}

export async function fetchHoldings(sessionId: string) {
  return request<{ holdings: Record<string, number> }>("/api/holdings", {}, sessionId);
}

export async function fetchPortfolioValue(sessionId: string) {
  return request<{ portfolio_value: number }>("/api/portfolio/value", {}, sessionId);
}

export async function fetchProfitLoss(sessionId: string) {
  return request<{ profit_loss: number }>("/api/portfolio/profit_loss", {}, sessionId);
}

export async function fetchTransactions(sessionId: string) {
  return request<{ transactions: Transaction[] }>("/api/transactions", {}, sessionId);
}
