import gradio as gr

from services import (
    buy,
    create_account,
    deposit,
    holdings,
    prices,
    sell,
    status,
    transactions,
    withdraw,
)
from session_store import SessionStore


store = SessionStore()


def _format_response(response):
    if response.get("success"):
        return response.get("message", "Success")
    return f"Error: {response.get('message', 'Request failed.')}"


def _format_status(token):
    response = status(store, token)
    if not response.get("success"):
        return _format_response(response)
    account = response["data"]["account"]
    pl = account["profit_loss"]
    pl_sign = "+" if pl >= 0 else ""
    return (
        f"Username: {account['username']}\n"
        f"Cash Balance: ${account['balance']:.2f}\n"
        f"Initial Deposit: ${account['initial_deposit']:.2f}\n"
        f"Total Portfolio Value: ${account['portfolio_value']:.2f}\n"
        f"Profit/Loss: {pl_sign}${pl:.2f}\n"
    )


def _format_holdings(token):
    response = holdings(store, token)
    if not response.get("success"):
        return _format_response(response)
    data = response["data"]
    holdings_map = data.get("holdings", {})
    if not holdings_map:
        return "No shares held."
    lines = ["Current Holdings:"]
    for symbol, quantity in holdings_map.items():
        value = data["holding_values"].get(symbol, 0.0)
        lines.append(f"  {symbol}: {quantity} shares = ${value:.2f}")
    return "\n".join(lines)


def _format_transactions(token):
    response = transactions(store, token)
    if not response.get("success"):
        return _format_response(response)
    items = response["data"].get("transactions", [])
    if not items:
        return "No transactions yet."
    lines = ["Transaction History:"]
    for index, entry in enumerate(items, 1):
        lines.append(f"{index}. {entry}")
    return "\n".join(lines)


def _format_prices():
    response = prices()
    data = response.get("data", {})
    symbols = data.get("symbols", {})
    lines = ["Current Share Prices:"]
    for symbol, price in symbols.items():
        lines.append(f"  {symbol}: ${price:.2f}")
    return "\n".join(lines)


def _create_account(username, initial_deposit):
    response = create_account(store, username, initial_deposit)
    token = response.get("data", {}).get("token") if response.get("success") else None
    return token, _format_response(response)


def _deposit(amount, token):
    return _format_response(deposit(store, token, amount))


def _withdraw(amount, token):
    return _format_response(withdraw(store, token, amount))


def _buy(symbol, quantity, token):
    return _format_response(buy(store, token, symbol, int(quantity)))


def _sell(symbol, quantity, token):
    return _format_response(sell(store, token, symbol, int(quantity)))


with gr.Blocks(title="Trading Account Demo") as demo:
    session_state = gr.State(value=None)

    gr.Markdown("# Trading Account Management System")
    gr.Markdown("Gradio control panel backed by session-aware services.")

    with gr.Tab("Create Account"):
        gr.Markdown("### Create New Account")
        with gr.Row():
            username_input = gr.Textbox(label="Username", value="Trader1")
            initial_deposit_input = gr.Number(label="Initial Deposit ($)", value=10000)
        create_btn = gr.Button("Create Account")
        create_output = gr.Textbox(label="Result", lines=2)
        create_btn.click(
            _create_account,
            inputs=[username_input, initial_deposit_input],
            outputs=[session_state, create_output],
        )

    with gr.Tab("Deposit/Withdraw"):
        gr.Markdown("### Manage Cash")
        with gr.Row():
            with gr.Column():
                deposit_amount = gr.Number(label="Deposit Amount ($)", value=1000)
                deposit_btn = gr.Button("Deposit")
                deposit_output = gr.Textbox(label="Result", lines=2)
                deposit_btn.click(
                    _deposit,
                    inputs=[deposit_amount, session_state],
                    outputs=deposit_output,
                )

            with gr.Column():
                withdraw_amount = gr.Number(label="Withdraw Amount ($)", value=500)
                withdraw_btn = gr.Button("Withdraw")
                withdraw_output = gr.Textbox(label="Result", lines=2)
                withdraw_btn.click(
                    _withdraw,
                    inputs=[withdraw_amount, session_state],
                    outputs=withdraw_output,
                )

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
                buy_btn.click(
                    _buy,
                    inputs=[buy_symbol, buy_quantity, session_state],
                    outputs=buy_output,
                )

            with gr.Column():
                gr.Markdown("#### Sell Shares")
                sell_symbol = gr.Textbox(label="Symbol", value="AAPL")
                sell_quantity = gr.Number(label="Quantity", value=5)
                sell_btn = gr.Button("Sell")
                sell_output = gr.Textbox(label="Result", lines=3)
                sell_btn.click(
                    _sell,
                    inputs=[sell_symbol, sell_quantity, session_state],
                    outputs=sell_output,
                )

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
                status_btn.click(_format_status, inputs=session_state, outputs=status_output)

            with gr.Column():
                holdings_output = gr.Textbox(label="Holdings", lines=8)
                holdings_btn.click(_format_holdings, inputs=session_state, outputs=holdings_output)

        with gr.Row():
            with gr.Column():
                transactions_output = gr.Textbox(label="Transaction History", lines=10)
                transactions_btn.click(
                    _format_transactions, inputs=session_state, outputs=transactions_output
                )

            with gr.Column():
                prices_output = gr.Textbox(label="Current Prices", lines=10)
                prices_btn.click(_format_prices, outputs=prices_output)


if __name__ == "__main__":
    demo.launch()
