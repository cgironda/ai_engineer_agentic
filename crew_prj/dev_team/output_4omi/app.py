import gradio as gr
from accounts import Account, get_share_price

# Initialize account for demonstration
account = Account(account_id="user_1", initial_deposit=1000.00)

def create_account(initial_deposit):
    global account
    account = Account(account_id="user_1", initial_deposit=initial_deposit)
    return f"Account created with initial deposit: ${initial_deposit:.2f}"

def deposit_funds(amount):
    account.deposit(amount)
    return f"Deposited: ${amount:.2f}. Current Balance: ${account.balance:.2f}"

def withdraw_funds(amount):
    try:
        account.withdraw(amount)
        return f"Withdrew: ${amount:.2f}. Current Balance: ${account.balance:.2f}"
    except ValueError as e:
        return str(e)

def buy_shares(symbol, quantity):
    try:
        account.buy_shares(symbol, quantity)
        return f"Bought: {quantity} shares of {symbol}. Current Balance: ${account.balance:.2f}"
    except ValueError as e:
        return str(e)

def sell_shares(symbol, quantity):
    try:
        account.sell_shares(symbol, quantity)
        return f"Sold: {quantity} shares of {symbol}. Current Balance: ${account.balance:.2f}"
    except ValueError as e:
        return str(e)

def portfolio_value():
    return f"Total Portfolio Value: ${account.get_portfolio_value():.2f}"

def profit_loss(initial_deposit):
    return f"Profit/Loss: ${account.calculate_profit_loss(initial_deposit):.2f}"

def holdings():
    return f"Current Holdings: {account.get_holdings()}"

def transactions():
    return f"Transactions: {account.list_transactions()}"

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("### Trading Account Management System")
    initial_deposit = gr.Number(label="Initial Deposit")
    create_btn = gr.Button("Create Account")
    create_btn.click(create_account, inputs=initial_deposit)

    deposit_amount = gr.Number(label="Deposit Amount")
    deposit_btn = gr.Button("Deposit Funds")
    deposit_btn.click(deposit_funds, inputs=deposit_amount)

    withdraw_amount = gr.Number(label="Withdraw Amount")
    withdraw_btn = gr.Button("Withdraw Funds")
    withdraw_btn.click(withdraw_funds, inputs=withdraw_amount)

    buy_symbol = gr.Textbox(label="Stock Symbol to Buy")
    buy_quantity = gr.Number(label="Quantity to Buy")
    buy_btn = gr.Button("Buy Shares")
    buy_btn.click(buy_shares, inputs=[buy_symbol, buy_quantity])

    sell_symbol = gr.Textbox(label="Stock Symbol to Sell")
    sell_quantity = gr.Number(label="Quantity to Sell")
    sell_btn = gr.Button("Sell Shares")
    sell_btn.click(sell_shares, inputs=[sell_symbol, sell_quantity])

    portfolio_value_btn = gr.Button("Get Portfolio Value")
    portfolio_value_btn.click(portfolio_value)

    initial_deposit_for_profit = gr.Number(label="Initial Deposit for Profit/Loss Calculation")
    profit_btn = gr.Button("Get Profit/Loss")
    profit_btn.click(profit_loss, inputs=initial_deposit_for_profit)

    holdings_btn = gr.Button("Get Current Holdings")
    holdings_btn.click(holdings)

    transactions_btn = gr.Button("List Transactions")
    transactions_btn.click(transactions)

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch()