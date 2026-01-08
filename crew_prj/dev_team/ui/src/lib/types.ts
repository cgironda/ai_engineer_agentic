export interface Transaction {
  type: string;
  symbol?: string | null;
  quantity?: number | null;
  price?: number | null;
  amount?: number | null;
  timestamp: string;
}

export interface AccountSnapshot {
  username: string;
  balance: number;
  holdings: Record<string, number>;
  portfolio_value: number;
  profit_or_loss: number;
  transactions: Transaction[];
}

export interface ApiResponse<T = Record<string, unknown>> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  session_id?: string;
}
