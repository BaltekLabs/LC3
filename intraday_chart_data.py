import requests
import pandas as pd
import io

API_KEY = '8XTSMCVVBO5CJLT9'

ba = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min&apikey=8XTSMCVVBO5CJLT9&datatype=csv')

df = pd.read_csv(io.StringIO(ba.text))  

for x in df.index:
    df.rename(index={x+1: ','}, inplace=True)
    
df.rename(index={0: ' '}, inplace=True)
#print(df.head())
#data_clean = pd.read_csv(data)
prices = df.close
prices.to_string(header=None,index=None)
print(prices)
#ba_res = ba.json()
#data = ba_res['Global Quote']

