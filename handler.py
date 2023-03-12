import ccxt
import json
import pandas as pd
import boto3

pd.set_option('display.max_rows', None)

coinbase_pro = ccxt.coinbasepro()
coinbase = ccxt.coinbase()

bucket_name = 'trade-store'

s3 = boto3.resource('s3')


def get_state(file_name):
    try:
        s3_object = s3.Object(bucket_name, file_name).get()
        jsonFileReader = s3_object['Body'].read()
        state = json.loads(jsonFileReader)
    except Exception as e:
        if e.response['Error']['Code'] == "NoSuchKey":
            print(f"creating {file_name} object")
            state = {"buying_power": 1000, "tokens": 0,
                     "history": [], "token_price": 0, 'uptrend': False}
            s3.Object(bucket_name, file_name).put(
                Body=json.dumps(state))
        else:
            raise e
    return state


def previously_uptrend(state):
    return state.get('uptrend')


def get_buying_power(state):
    return state.get('buying_power')


def set_buying_power(state, amount):
    state['buying_power'] = amount
    return state


def get_tokens(state):
    return state.get('tokens')


def set_tokens(state, amount):
    state['tokens'] = amount
    return state


def get_token_price(state):
    return state.get('token_price')


def set_token_price(state, token_price):
    state['token_price'] = token_price
    return state


def get_state_snapshot(state):
    return {
        'buying_power': get_buying_power(state),
        'tokens': get_tokens(state),
        'token_price': get_token_price(state),
    }


def push_history(state, timestamp, snapshot):
    if state.get('history') is None:
        state['history'] = []
    state['history'].append({'timestamp': timestamp, 'snapshot': snapshot})
    return state


def get_signal(state, df):
    currently_uptrend = df.iloc[-1]['uptrend']
    if currently_uptrend and not previously_uptrend(state):
        return 'buy'
    elif not currently_uptrend and previously_uptrend(state):
        return 'sell'
    else:
        return 'hold'


def set_uptrend(state, uptrend):
    state['uptrend'] = uptrend
    return state


def exec_buy(state, num_tokens, conversion):
    state['tokens'] = state.get("tokens") + num_tokens
    state['buying_power'] = state.get(
        "buying_power") - (num_tokens * conversion)
    return state


def exec_sell(state, num_tokens, conversion):
    state['tokens'] = state.get("tokens") - num_tokens
    state['buying_power'] = state.get(
        "buying_power") + (num_tokens * conversion)
    return state


def save_state(state, file_name):
    s3.Object(bucket_name, file_name).put(
        Body=json.dumps(state))


def current_token_price(df):
    return df.iloc[-1]['close']


def current_timestamp(df):
    timestamp = df.iloc[-1]['timestamp']
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def run_strategy(state_file_name, buy_sell_fraction=0.2, period=7, limit=100, timeframe='15m', multiplier=3):
    state = get_state(state_file_name)
    df = supertrend(period, limit, timeframe, multiplier)
    signal = get_signal(state, df)
    token_price = current_token_price(df)
    buying_power = get_buying_power(state)
    tokens = get_tokens(state)
    state_snapshot = get_state_snapshot(state)
    if signal == 'buy':
        balance_in_tokens = buying_power / token_price
        buy_amount = balance_in_tokens * buy_sell_fraction
        state = exec_buy(set_uptrend(state, True), buy_amount, token_price)
    elif signal == 'sell':
        sell_amount = tokens * buy_sell_fraction
        state = exec_sell(set_uptrend(state, False), sell_amount, token_price)

    if signal == 'buy' or signal == 'sell':
        buying_power = get_buying_power(state)
        tokens = get_tokens(state)
        state = push_history(set_token_price(state, token_price),
                             current_timestamp(df), state_snapshot)
        save_state(state, state_file_name)

    return {
        'signal': signal,
        'buying_power': buying_power,
        'tokens': tokens,
    }


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


def run_1h_at_10(event, context):
    body = run_strategy('state_7-200-1h-2.json', 0.1, 7, 200, '1h', 2)

    return {
        'statusCode': 200,
        'body': body
    }


def run_1h_at_95(event, context):
    body = run_strategy('state_95-7-200-1h-2.json', 0.95, 7, 200, '1h', 2)

    return {
        'statusCode': 200,
        'body': body
    }


def run_1m_at_10(event, context):
    body = run_strategy('state_7-200-1m-2.json', 0.1, 7, 200, '1m', 2)

    return {
        'statusCode': 200,
        'body': body
    }


def run_1m_at_95(event, context):
    body = run_strategy('state_95-7-200-1m-2.json', 0.95, 7, 200, '1m', 2)

    return {
        'statusCode': 200,
        'body': body
    }
