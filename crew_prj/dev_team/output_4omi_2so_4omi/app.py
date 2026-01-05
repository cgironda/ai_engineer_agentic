import gradio as gr
from accounts import Account, get_share_price

# Initialize a single user account (persistent across UI interactions)
account = None

def create_account(username, initial_deposit):
    global account
    try:
        if initial_deposit <= 0:
            return "Error: Initial deposit must be greater than zero."
        account = Account(username, initial_deposit)
        return f"Account created for {username} with initial deposit of ${initial_deposit:.2f}"
    except Exception as e:
        return f"Error: {str(e)}"

def deposit_funds(amount):
    global account
    try:
        if account is None:
            return "Error: Please create an account first."
        account.deposit(amount)
        return f"Successfully deposited ${amount:.2f}. New balance: ${account.balance:.2f}"
    except Exception as e:
        return f"Error: {str(e)}"

def withdraw_funds(amount):
    global account
    try:
        if account is None:
            return "Error: Please create an account first."
        account.withdraw(amount)
        return f"Successfully withdrew ${amount:.2f}. New balance: ${account.balance:.2f}"
    except Exception as e:
        return f"Error: {str(e)}"

def buy_shares(symbol, quantity):
    global account
    try:
        if account is None:
            return "Error: Please create an account first."
        price = get_share_price(symbol)
        if price == 0.0:
            return f"Error: Unknown symbol '{symbol}'. Available: AAPL, TSLA, GOOGL"
        account.buy_shares(symbol, int(quantity))
        return f"Successfully bought {quantity} shares of {symbol} at ${price:.2f} each. Total: ${price * quantity:.2f}"
    except Exception as e:
        return f"Error: {str(e)}"

def sell_shares(symbol, quantity):
    global account
    try:
        if account is None:
            return "Error: Please create an account first."
        price = get_share_price(symbol)
        account.sell_shares(symbol, int(quantity))
        return f"Successfully sold {quantity} shares of {symbol} at ${price:.2f} each. Total: ${price * quantity:.2f}"
    except Exception as e:
        return f"Error: {str(e)}"

def view_account_status():
    global account
    if account is None:
        return "No account created yet."
    
    portfolio_value = account.calculate_portfolio_value()
    profit_loss = account.calculate_profit_loss()
    pl_sign = "+" if profit_loss >= 0 else ""
    
    status = f"Username: {account.username}\n"
    status += f"Cash Balance: ${account.balance:.2f}\n"
    status += f"Initial Deposit: ${account.initial_deposit:.2f}\n"
    status += f"Total Portfolio Value: ${portfolio_value:.2f}\n"
    status += f"Profit/Loss: {pl_sign}${profit_loss:.2f}\n"
    
    return status

def view_holdings():
    global account
    if account is None:
        return "No account created yet."
    
    holdings = account.report_holdings()
    if not holdings:
        return "No shares held."
    
    output = "Current Holdings:\n"
    for symbol, quantity in holdings.items():
        price = get_share_price(symbol)
        value = price * quantity
        output += f"  {symbol}: {quantity} shares @ ${price:.2f} = ${value:.2f}\n"
    
    return output

def view_transactions():
    global account
    if account is None:
        return "No account created yet."
    
    transactions = account.report_transactions()
    if not transactions:
        return "No transactions yet."
    
    output = "Transaction History:\n"
    for i, transaction in enumerate(transactions, 1):
        output += f"{i}. {transaction}\n"
    
    return output

def view_share_prices():
    prices = "Current Share Prices:\n"
    for symbol in ['AAPL', 'TSLA', 'GOOGL']:
        price = get_share_price(symbol)
        prices += f"  {symbol}: ${price:.2f}\n"
    return prices

# Create Gradio interface
with gr.Blocks(title="Trading Account Demo") as demo:
    gr.Markdown("# Trading Account Management System")
    gr.Markdown("A simple demo for managing a single trading account")
    
    with gr.Tab("Create Account"):
        gr.Markdown("### Create New Account")
        with gr.Row():
            username_input = gr.Textbox(label="Username", value="Trader1")
            initial_deposit_input = gr.Number(label="Initial Deposit ($)", value=10000)
        create_btn = gr.Button("Create Account")
        create_output = gr.Textbox(label="Result", lines=2)
        create_btn.click(create_account, inputs=[username_input, initial_deposit_input], outputs=create_output)
    
    with gr.Tab("Deposit/Withdraw"):
        gr.Markdown("### Manage Cash")
        with gr.Row():
            with gr.Column():
                deposit_amount = gr.Number(label="Deposit Amount ($)", value=1000)
                deposit_btn = gr.Button("Deposit")
                deposit_output = gr.Textbox(label="Result", lines=2)
                deposit_btn.click(deposit_funds, inputs=deposit_amount, outputs=deposit_output)
            
            with gr.Column():
                withdraw_amount = gr.Number(label="Withdraw Amount ($)", value=500)
                withdraw_btn = gr.Button("Withdraw")
                withdraw_output = gr.Textbox(label="Result", lines=2)
                withdraw_btn.click(withdraw_funds, inputs=withdraw_amount, outputs=withdraw_output)
    
    with gr.Tab("Trade Shares"):
        gr.Markdown("### Buy/Sell Shares")
        gr.Markdown("Available symbols: AAPL, TSLA, GOOGL")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Buy Shares")
                buy_symbol = gr.Textbox(label="Symbol", value="AAPL")
                buy_quantity = gr.Number(label="Quantity", value=10)
                buy_btn = gr.Button("Buy")
                buy_output = gr.Textbox(label="Result", lines=3)
                buy_btn.click(buy_shares, inputs=[buy_symbol, buy_quantity], outputs=buy_output)
            
            with gr.Column():
                gr.Markdown("#### Sell Shares")
                sell_symbol = gr.Textbox(label="Symbol", value="AAPL")
                sell_quantity = gr.Number(label="Quantity", value=5)
                sell_btn = gr.Button("Sell")
                sell_output = gr.Textbox(label="Result", lines=3)
                sell_btn.click(sell_shares, inputs=[sell_symbol, sell_quantity], outputs=sell_output)
    
    with gr.Tab("View Account"):
        gr.Markdown("### Account Information")
        
        with gr.Row():
            status_btn = gr.Button("Refresh Account Status")
            holdings_btn = gr.Button("Refresh Holdings")
            transactions_btn = gr.Button("Refresh Transactions")
            prices_btn = gr.Button("View Share Prices")
        
        with gr.Row():
            with gr.Column():
                status_output = gr.Textbox(label="Account Status", lines=8)
                status_btn.click(view_account_status, outputs=status_output)
            
            with gr.Column():
                holdings_output = gr.Textbox(label="Holdings", lines=8)
                holdings_btn.click(view_holdings, outputs=holdings_output)
        
        with gr.Row():
            with gr.Column():
                transactions_output = gr.Textbox(label="Transaction History", lines=10)
                transactions_btn.click(view_transactions, outputs=transactions_output)
            
            with gr.Column():
                prices_output = gr.Textbox(label="Current Prices", lines=10)
                prices_btn.click(view_share_prices, outputs=prices_output)

if __name__ == "__main__":
    demo.launch()