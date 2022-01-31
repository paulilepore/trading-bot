
import websocket, json, pprint, talib, numpy
from dotenv import load_dotenv
from binance.client import Client
from binance.enums import *
import os

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
# Overbought indicator
RSI_OVERBOUGHT = 70
# Oversold indicator
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.009

# Closes will be collected in a list
closes = []
# Don't own currency
in_position = False

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

client = Client(api_key,api_secret)

# Make an order(BUY OR SELL)
def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        # Sending order to binance
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("An exception occured - {}".format(e))
        return False
    return True

def on_open(ws):
    print('open connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position

    print('received message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        # Print out candle closing data
        print("Candle closed at {}".format(close))
        closes.append(float(close))
        print("Closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("All rsi calculated")
            print(rsi)
            last_rsi = rsi[-1]
            print("The current rsi is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Sell !!")
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("Overbought, but we dont owe any. Do nothing")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold but you own it, do nothing")
                else:
                    print("BUYYYY!!")
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True



ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
