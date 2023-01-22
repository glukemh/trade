import ccxt
import json
import pandas as pd

pd.set_option('display.max_rows', None)

coinbase_pro = ccxt.coinbasepro()
coinbase = ccxt.coinbase()


def supertrend(period=7, limit=10, timeframe='15m', multiplier=3):
    bars = coinbase_pro.fetch_ohlcv(
        'ETH/USD', timeframe=timeframe, since=None, limit=limit)
    df = pd.DataFrame(bars, columns=['timestamp',
                      'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['previous_close'] = df['close'].shift(1)
    df['abs(h-l)'] = (df['high'] - df['low']).abs()
    df['abs(h-pc)'] = (df['high'] - df['previous_close']).abs()
    df['abs(l-pc)'] = (df['low'] - df['previous_close']).abs()
    df['tr'] = df[['abs(h-l)', 'abs(h-pc)', 'abs(l-pc)']].max(axis=1)
    df['atr'] = df['tr'].rolling(period).mean()
    hl_ave = (df['high'] + df['low']) / 2
    atr_multiple = multiplier * df['atr']
    df['basic_upper_band'] = hl_ave + atr_multiple
    df['basic_lower_band'] = hl_ave - atr_multiple
    df['uptrend'] = True
    df['upper_band'] = float('inf')
    df['lower_band'] = float('-inf')

    for i in range(1, len(df)):
        current = df.iloc[i]
        previous = df.iloc[i-1]

        if current['close'] > previous['basic_upper_band']:
            df.loc[i, 'uptrend'] = True
        elif current['close'] < previous['basic_lower_band']:
            df.loc[i, 'uptrend'] = False
        else:
            df.loc[i, 'uptrend'] = previous['uptrend']

        current = df.iloc[i]
        if current['uptrend']:
            df.loc[i, 'lower_band'] = max(
                current['basic_lower_band'], previous['lower_band'])
        else:
            df.loc[i, 'upper_band'] = min(
                current['basic_upper_band'], previous['upper_band'])

    return df


print(supertrend(7, 200, '1h', 2))


def run(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
