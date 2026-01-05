import gradio as gr
from accounts import Account, get_share_price

def create_account(username, initial_deposit):
    global account
    account = Account(username, initial_deposit)
    return f"Account for {username} created with initial deposit of ${initial_deposit}."

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

app = gr.Interface(
    fn=lambda username, initial_deposit, amount, symbol, quantity, action: eval(action)(),
    inputs=[
        gr.inputs.Textbox(label="Username"),
        gr.inputs.Number(label="Initial Deposit"),
        gr.inputs.Number(label="Amount for Deposit/Withdraw"),
        gr.inputs.Textbox(label="Symbol for Buy/Sell"),
        gr.inputs.Number(label="Quantity for Buy/Sell"),
        gr.inputs.Radio(choices=[
            "create_account(username, initial_deposit)",
            "deposit_funds(amount)",
            "withdraw_funds(amount)",
            "buy_shares(symbol, quantity)",
            "sell_shares(symbol, quantity)",
            "get_portfolio_value()",
            "get_profit_or_loss()",
            "view_holdings()",
            "view_transactions()"
        ], label="Action")
    ],
    outputs="text"
)

app.launch()