import os
from kit_trade import KiteApp
import datetime
import time

# Order placement is OFF unless KITE_PLACE_ORDERS=1 is set in the environment.
PLACE_ORDERS = os.environ.get('KITE_PLACE_ORDERS') == '1'

# Function to check if the stochastic oscillator signals a buy
def check_stochastic_buy(stoch):
    if stoch > 80:  # Buy when the stochastic oscillator is above 80 (overbought condition)
        return True
    else:
        return False

# Function to check if the stochastic oscillator signals a sell
def check_stochastic_sell(stoch):
    if stoch < 20:  # Sell when the stochastic oscillator is below 20 (oversold condition)
        return True
    else:
        return False

# Function to place (or, by default, only describe) a market order for 1 unit of GOLDBEES
def place_market_order(transaction_type):
    if not PLACE_ORDERS:
        return "DRY RUN: no order sent (set KITE_PLACE_ORDERS=1 to send real orders)"
    return kite.place_order(variety=kite.VARIETY_REGULAR,
                            exchange=kite.EXCHANGE_NSE,
                            tradingsymbol="GOLDBEES",
                            transaction_type=transaction_type,
                            quantity=1,
                            product=kite.PRODUCT_MIS,
                            order_type=kite.ORDER_TYPE_MARKET,
                            price=None,
                            validity=None,
                            disclosed_quantity=None,
                            trigger_price=None,
                            squareoff=None,
                            stoploss=None,
                            trailing_stoploss=None,
                            tag="TradeViaPython")

# Session token is read from the environment, never stored in the source (see README).
enctoken = os.environ.get('KITE_ENCTOKEN')
if not enctoken:
    raise SystemExit('Set the KITE_ENCTOKEN environment variable first (see README).')
# Initialize KiteApp object with the encrypted token
kite = KiteApp(enctoken=enctoken)

# Define instrument token and time interval
instrument_token = 3693569  # Replace with the instrument token of your choice
interval = "5minute"        # Interval for data (e.g., 5-minute intervals)

# Main loop to run the strategy every 5 minutes
while True:
    try:
        # Fetch the last 7 days of candles. The window is recomputed on every pass
        # (the original computed it once, so the data went stale while the loop ran).
        from_datetime = datetime.datetime.now() - datetime.timedelta(days=7)
        to_datetime = datetime.datetime.now()
        historical_data = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)

        # Check if historical data is available
        if historical_data:
            # Calculate stochastic oscillator (%K) from the closes in the window
            close_prices = [candle['close'] for candle in historical_data]
            lowest_low = min(close_prices)
            highest_high = max(close_prices)
            current_close = close_prices[-1]
            if highest_high == lowest_low:
                stoch = 50.0  # flat window: avoid ZeroDivisionError, treat as neutral
            else:
                stoch = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100

            # Check for buy signal
            if check_stochastic_buy(stoch):
                order = place_market_order(kite.TRANSACTION_TYPE_BUY)
                print("Buy signal at", datetime.datetime.now(), "stoch =", round(stoch, 1))
                print("Order details:", order)

            # Check for sell signal
            elif check_stochastic_sell(stoch):
                order = place_market_order(kite.TRANSACTION_TYPE_SELL)
                print("Sell signal at", datetime.datetime.now(), "stoch =", round(stoch, 1))
                print("Order details:", order)

        else:
            print("Historical data is empty")

    except Exception as e:
        print("Error:", e)

    # Sleep for 5 minutes (the original only slept on success, so an error caused a tight retry loop)
    time.sleep(300)
