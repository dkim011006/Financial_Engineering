import yfinance as yf
import pandas as pd

data = yf.download('^GSPC',start = '1927-12-30',end='2020-11-09')

data.to_excel('history.xlsx')