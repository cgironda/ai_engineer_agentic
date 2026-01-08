export type ApiResponse<T> = {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
};

export type AccountSummary = {
  username: string;
  balance: number;
  initial_deposit: number;
  portfolio_value: number;
  profit_loss: number;
};

export type HoldingSnapshot = {
  holdings: Record<string, number>;
  holding_values: Record<string, number>;
};

export type TradeSnapshot = {
  symbol: string;
  quantity: number;
  price: number;
  total: number;
};

export type CreateAccountData = {
  token: string;
  account: AccountSummary;
  holdings: HoldingSnapshot;
};

export type AccountData = {
  account: AccountSummary;
};

export type HoldingsData = AccountData & HoldingSnapshot;

export type TransactionsData = AccountData & { transactions: string[] };

export type PricesData = { symbols: Record<string, number> };
