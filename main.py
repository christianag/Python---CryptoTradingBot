from binance import client
from binance.client import Client
from binance import BinanceSocketManager
from pandas._config import config
from config import Keys

import config
import pandas as pd
import sqlalchemy


client = Client(api_key=Keys.apiKey, api_secret=Keys.apiSecret)

# datastream via websocket 
def get_minute_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + ' min ago GMT+2'))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

def strategy_test(symbol, qty, entried=False):

    df = get_minute_data(symbol, '1m', '30m')
    cumulret = (df.Open.pct_change() + 1).cumprod() - 1

    if not entried: 
        if cumulret[-1] < 0.002:
            order = client.create_order(symbol=symbol, side='BUY', type='MARKET',  quantity=qty)
            print(order)
            entried = True
        else:
            print("No trade has been executed")
        
    if entried:
        while True:
            df = get_minute_data(symbol, '1m', '30m')
            sincebuy = df.loc[df.index > pd.to_datetime(order['transactTime'], unit='ms')]
            if len(sincebuy) > 0:
                sincebuyret = (sincebuy.Open.pct_change() + 1).cumprod() - 1
                if sincebuyret[-1] > 0.0015 or sincebuyret[-1] < -0.0015:
                    order = client.create_order(symbol=symbol, side='SELL', type='MARKET',  quantity=qty)
                    print(order)
                    break 


# strategy_test('BTCUSDT', 0.00001)
print(get_minute_data('BTCUSDT', '1m', '30m'))
