import json
import pandas as pd
import ccxt


def run(event, context):
    print('pd.__version__:', pd.__version__)
    print('ccxt.__version__:', ccxt.__version__)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
