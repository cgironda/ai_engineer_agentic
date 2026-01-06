import gradio as gr
from accounts import Account, get_share_price

def create_account(username, initial_deposit):
    global account
    deposit = initial_deposit or 0.0
    account = Account(username, deposit)
    return f"Account for {username} created. Balance: ${account.balance}"

def deposit_funds(amount):
    if account:
        account.deposit(amount)
        return f"Deposited ${amount}. New balance: ${account.balance}"
    return "No account found."

def withdraw_funds(amount):
    if account and account.withdraw(amount):
        return f"Withdrew ${amount}. New balance: ${account.balance}"
    return "Insufficient funds or no account found."

def buy_shares(symbol, quantity):
    if account and account.buy_shares(symbol, quantity, get_share_price):
        return f"Bought {quantity} shares of {symbol}."
    return "Insufficient funds or no account found."

def sell_shares(symbol, quantity):
    if account and account.sell_shares(symbol, quantity, get_share_price):
        return f"Sold {quantity} shares of {symbol}."
    return "Insufficient shares or no account found."

def get_portfolio_value():
    if account:
        value = account.calculate_portfolio_value(get_share_price)
        return f"Portfolio total value: ${value}"
    return "No account found."

def get_profit_or_loss():
    if account:
        profit_loss = account.calculate_profit_or_loss(get_share_price)
        return f"Profit/Loss: ${profit_loss}"
    return "No account found."

def view_holdings():
    if account:
        holdings = account.report_holdings()
        return f"Current Holdings: {holdings}"
    return "No account found."

def view_transactions():
    if account:
        transactions = account.list_transactions()
        return f"Transactions: {transactions}"
    return "No account found."

account = None

def handle_action(username, initial_deposit, amount, symbol, quantity, action):
    try:
        if action == "create_account":
            return create_account(username, initial_deposit)
        if action == "deposit_funds":
            return deposit_funds(amount)
        if action == "withdraw_funds":
            return withdraw_funds(amount)
        if action == "buy_shares":
            return buy_shares(symbol, quantity)
        if action == "sell_shares":
            return sell_shares(symbol, quantity)
        if action == "get_portfolio_value":
            return get_portfolio_value()
        if action == "get_profit_or_loss":
            return get_profit_or_loss()
        if action == "view_holdings":
            return view_holdings()
        if action == "view_transactions":
            return view_transactions()
        return "Unknown action."
    except ValueError as exc:
        return str(exc)

app = gr.Interface(
    fn=handle_action,
    inputs=[
        gr.Textbox(label="Username"),
        gr.Number(label="Initial Deposit"),
        gr.Number(label="Amount for Deposit/Withdraw"),
        gr.Textbox(label="Symbol for Buy/Sell"),
        gr.Number(label="Quantity for Buy/Sell"),
        gr.Radio(
            choices=[
                "create_account",
                "deposit_funds",
                "withdraw_funds",
                "buy_shares",
                "sell_shares",
                "get_portfolio_value",
                "get_profit_or_loss",
                "view_holdings",
                "view_transactions",
            ],
            label="Action",
        ),
    ],
    outputs="text",
)

app.launch()
