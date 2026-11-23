import os
from kit_trade import KiteApp
import datetime
import time

# Order placement is OFF unless KITE_PLACE_ORDERS=1 is set in the environment.
PLACE_ORDERS = os.environ.get('KITE_PLACE_ORDERS') == '1'

# Function to check if the moving average crossover strategy signals a buy
def check_buy_signal(short_ma_values, long_ma_values):
    if not short_ma_values or not long_ma_values:
        return False  # not enough data yet (the original raised ZeroDivisionError here)
    short_ma_avg = sum(short_ma_values) / len(short_ma_values)
    long_ma_avg = sum(long_ma_values) / len(long_ma_values)
    if short_ma_avg > long_ma_avg:
        return True
    else:
        return False

# Function to fetch historical data
def fetch_historical_data(instrument_token, from_datetime, to_datetime, interval):
    return kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)

# Function to place (or, by default, only describe) a market buy of 1 unit of GOLDBEES
def place_buy_order():
    if not PLACE_ORDERS:
        return "DRY RUN: no order sent (set KITE_PLACE_ORDERS=1 to send real orders)"
    return kite.place_order(variety=kite.VARIETY_REGULAR,
                            exchange=kite.EXCHANGE_NSE,
                            tradingsymbol="GOLDBEES",
                            transaction_type=kite.TRANSACTION_TYPE_BUY,
                            quantity=1,
                            product=kite.PRODUCT_MIS,
                            order_type=kite.ORDER_TYPE_MARKET,
                            tag="TradeViaPython")

# Session token is read from the environment, never stored in the source (see README).
enctoken = os.environ.get('KITE_ENCTOKEN')
if not enctoken:
    raise SystemExit('Set the KITE_ENCTOKEN environment variable first (see README).')
# Initialize KiteApp object with the encrypted token
kite = KiteApp(enctoken=enctoken)

# Define instrument token and time interval
instrument_token = 3693569  # Replace with the instrument token of your choice
interval = "5minute"  # Adjust interval as needed (e.g., "1day", "15minute", etc.)

# Define parameters for moving averages and time interval
short_term_ma_period = 10
long_term_ma_period = 20
interval_seconds = 60  # Check for buy signal every 60 seconds
total_runtime_hours = 10
start_time = time.time()
end_time = start_time + (total_runtime_hours * 60 * 60)
no_buy_signal_interval = 60  # Print message if no buy signal is found every 60 seconds
no_buy_signal_timer = time.time() + no_buy_signal_interval

# Lists to store moving average values
short_ma_values = []
long_ma_values = []

# Main loop to run the strategy for the specified duration
while time.time() < end_time:
    try:
        # Fetch historical data
        from_datetime = datetime.datetime.now() - datetime.timedelta(days=7)
        to_datetime = datetime.datetime.now()
        historical_data = fetch_historical_data(instrument_token, from_datetime, to_datetime, interval)

        # Extract close prices for calculation of moving averages
        close_prices = [candle['close'] for candle in (historical_data or [])]

        # Update moving average lists
        if len(close_prices) >= long_term_ma_period:
            short_ma_values.append(sum(close_prices[-short_term_ma_period:]) / short_term_ma_period)
            long_ma_values.append(sum(close_prices[-long_term_ma_period:]) / long_term_ma_period)

            # Keep the moving average lists within their respective periods
            if len(short_ma_values) > short_term_ma_period:
                short_ma_values.pop(0)
            if len(long_ma_values) > long_term_ma_period:
                long_ma_values.pop(0)

        # Check for buy signal
        if check_buy_signal(short_ma_values, long_ma_values):
            # Place Buy Order for 1 Unit of GOLDBEES (the original never defined `order`; see place_buy_order)
            order = place_buy_order()

            print("Buy signal at", datetime.datetime.now())
            print("Order details:", order)

            # Reset the no buy signal timer
            no_buy_signal_timer = time.time() + no_buy_signal_interval

    except Exception as e:
        print("Error:", e)

    # Check if no buy signal is found and print a message
    if time.time() >= no_buy_signal_timer:
        print("No buy signal found at", datetime.datetime.now())
        no_buy_signal_timer = time.time() + no_buy_signal_interval

    # Wait for the specified interval before the next iteration
    time.sleep(interval_seconds)
