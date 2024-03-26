from kite_trade import KiteApp
import datetime
import time

# Function to check if the moving average crossover strategy signals a buy
def check_buy_signal(ma_short, ma_long):
    if ma_short > ma_long:
        return True
    else:
        return False

# Replace 'enctoken' with your actual encrypted token
enctoken = '/ba+VmUolzQByvCBW/iHBfqb4LFxfpr0QTXdMz2bwBBWLXvDkUQtyQIWYTrxunYxSIdP0vL64kwfo1+tsV8JTeiOSlGoqS65axA7D1HXABU7R+QHf0ywog=='
# Initialize KiteApp object with the encrypted token
kite = KiteApp(enctoken=enctoken)

# Define instrument token and time interval
instrument_token = 3693569  # Replace with the instrument token of your choice
from_datetime = datetime.datetime.now() - datetime.timedelta(days=7)
to_datetime = datetime.datetime.now()
interval = "5minute"  # Adjust interval as needed (e.g., "1day", "15minute", etc.)

# Define parameters for moving averages and time interval
short_term_ma_period = 10
long_term_ma_period = 20
interval_seconds = 1  # Fetch market data every second
total_runtime_hours = 10
start_time = time.time()
end_time = start_time + (total_runtime_hours * 60 * 60)

# Main loop to run the strategy for the specified duration
while time.time() < end_time:
    try:
        # Fetch historical data
        historical_data = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
        
        # Calculate moving averages
        short_term_ma = sum(candle['close'] for candle in historical_data[-short_term_ma_period:]) / short_term_ma_period
        long_term_ma = sum(candle['close'] for candle in historical_data[-long_term_ma_period:]) / long_term_ma_period

        # Check for buy signal
        if check_buy_signal(short_term_ma, long_term_ma):
            # Place Buy Order for 1 Unit of GOLDBEES
            order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                     exchange=kite.EXCHANGE_NSE,
                                     tradingsymbol="GOLDBEES",
                                     transaction_type=kite.TRANSACTION_TYPE_BUY,
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

            print("Buy order placed at", datetime.datetime.now())
            print("Order details:", order)

    except Exception as e:
        print("Error:", e)
