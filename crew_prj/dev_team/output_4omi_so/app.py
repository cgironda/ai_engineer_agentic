import gradio as gr
from accounts import Account, get_share_price

# Create a single user account for demonstration
user_account = Account(user_name="DemoUser", initial_deposit=10000.0)

def create_account(name, initial_deposit):
    global user_account
    user_account = Account(user_name=name, initial_deposit=float(initial_deposit))
    return f"Account created for {name} with an initial deposit of ${initial_deposit}."

def deposit_funds(amount):
    user_account.deposit(float(amount))
    return f"Deposited ${amount}. New balance: ${user_account.balance:.2f}."

def withdraw_funds(amount):
    try:
        user_account.withdraw(float(amount))
        return f"Withdrew ${amount}. New balance: ${user_account.balance:.2f}."
    except ValueError as e:
        return str(e)

def buy_shares(symbol, quantity):
    try:
        user_account.buy_shares(symbol, int(quantity))
        return f"Bought {quantity} shares of {symbol}. New balance: ${user_account.balance:.2f}."
    except ValueError as e:
        return str(e)

def sell_shares(symbol, quantity):
    try:
        user_account.sell_shares(symbol, int(quantity))
        return f"Sold {quantity} shares of {symbol}. New balance: ${user_account.balance:.2f}."
    except ValueError as e:
        return str(e)

def portfolio_value():
    return f"Total portfolio value: ${user_account.get_portfolio_value():.2f}"

def profit_loss():
    return f"Profit/Loss: ${user_account.get_profit_loss():.2f}"

def holdings():
    return user_account.list_holdings()

def transactions():
    return user_account.list_transactions()

with gr.Blocks() as demo:
    gr.Markdown("# Trading Simulation Account Management")
    
    with gr.Tab("Account Management"):
        name_input = gr.Textbox(label="Account Name")
        initial_deposit_input = gr.Number(label="Initial Deposit", value=10000)
        create_button = gr.Button("Create Account")
        create_output = gr.Textbox(label="Output", interactive=False)
        
        create_button.click(create_account, inputs=[name_input, initial_deposit_input], outputs=create_output)
        
        deposit_input = gr.Number(label="Deposit Amount")
        deposit_button = gr.Button("Deposit")
        deposit_output = gr.Textbox(label="Output", interactive=False)
        
        deposit_button.click(deposit_funds, inputs=deposit_input, outputs=deposit_output)
        
        withdraw_input = gr.Number(label="Withdrawal Amount")
        withdraw_button = gr.Button("Withdraw")
        withdraw_output = gr.Textbox(label="Output", interactive=False)
        
        withdraw_button.click(withdraw_funds, inputs=withdraw_input, outputs=withdraw_output)

    with gr.Tab("Trading"):
        symbol_input = gr.Textbox(label="Stock Symbol (e.g. AAPL)")
        quantity_input = gr.Number(label="Quantity")
        buy_button = gr.Button("Buy Shares")
        sell_button = gr.Button("Sell Shares")
        trading_output = gr.Textbox(label="Output", interactive=False)
        
        buy_button.click(buy_shares, inputs=[symbol_input, quantity_input], outputs=trading_output)
        sell_button.click(sell_shares, inputs=[symbol_input, quantity_input], outputs=trading_output)

    with gr.Tab("Portfolio"):
        portfolio_button = gr.Button("Get Portfolio Value")
        portfolio_output = gr.Textbox(label="Output", interactive=False)
        profit_loss_button = gr.Button("Get Profit/Loss")
        profit_loss_output = gr.Textbox(label="Output", interactive=False)
        holdings_button = gr.Button("List Holdings")
        holdings_output = gr.Textbox(label="Output", interactive=False)
        transactions_button = gr.Button("List Transactions")
        transactions_output = gr.Textbox(label="Output", interactive=False)
        
        portfolio_button.click(portfolio_value, outputs=portfolio_output)
        profit_loss_button.click(profit_loss, outputs=profit_loss_output)
        holdings_button.click(holdings, outputs=holdings_output)
        transactions_button.click(transactions, outputs=transactions_output)

demo.launch()