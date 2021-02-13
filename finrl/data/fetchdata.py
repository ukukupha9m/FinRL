"""Contains methods and classes to collect data from
Yahoo Finance API
"""

import pandas as pd
import yfinance as yf
from finrl.exceptions import *
import os
import sys
import glob
from datetime import datetime

class FetchData:
    """Provides methods for retrieving daily stock data from
    Yahoo Finance API

    Attributes
    ----------
    start_date : str
        start date of the data (modified from config.py)
        
    end_date : str
        end date of the data (modified from config.py)
            
    ticker_list : list
        a list of stock tickers (modified from config.py)

    Methods
    -------
    fetch_data()
        Fetches data from yahoo API

    """

    def __init__(self, config: dict):
        self.config = config

    def fetch_data_stock(self) -> pd.DataFrame:
        """Fetches data from Yahoo API
        
        Parameters
        ----------

        Returns
        -------
        `pd.DataFrame`
            7 columns: A date, open, high, low, close, volume and tick symbol
            for the specified stock ticker
        """
        exchange = "yahoo"
        datadir = f'{self.config["user_data_dir"]}/data/{exchange}'
        print(datadir)
        timeframe = self.config["timeframe"]
        ticker_list = self.config["ticker_list"]
        # Download and save the data in a pandas DataFrame:
        data_df = pd.DataFrame()
        for i in ticker_list:
            temp_df = pd.read_json(f'{os.getcwd()}/{datadir}/{i}.json')
            temp_df["tic"] = i
            data_df = data_df.append(temp_df)
        # reset the index, we want to use numbers as index instead of dates
        data_df = data_df.reset_index()
        try:
            # convert the column names to standardized names
            data_df.columns = [
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "tic",
            ]
        except NotImplementedError:
            print("the features are not supported currently")
        # create day of the week column (monday = 0)
        data_df["day"] = data_df["date"].dt.dayofweek
        # convert date to standard string format, easy to filter
        data_df["date"] = data_df.date.apply(lambda x: x.strftime("%Y-%m-%d"))
        # drop missing data
        data_df = data_df.dropna()
        data_df = data_df.reset_index(drop=True)
        print("Shape of DataFrame: ", data_df.shape)
        # print("Display DataFrame: ", data_df.head())

        data_df = data_df.sort_values(by=['date','tic']).reset_index(drop=True)
        print(data_df.head())
        return data_df

    def fetch_data_crypto(self) -> pd.DataFrame:
        """
        Fetches data from local history directory (default= user_data/data/exchange)
        
        Parameters
        ----------
        config.json ---> Exchange, Whitelist, timeframe 

        Returns
        -------
        `pd.DataFrame`
            7 columns: A date, open, high, low, close, volume and tick symbol
            for the specified stock ticker
        """

        datadir = self.config['datadir']
        exchange = self.config["exchange"]["name"]
        timeframe = self.config["timeframe"]
        # Check if regex found something and only return these results
        df = pd.DataFrame()
        for i in self.config["pairs"]:
            i = i.replace("/","_")
            try:
                i_df = pd.read_json(f'{os.getcwd()}/{datadir}/{i}-{timeframe}.json')
                i_df["tic"] = i
                i_df.columns = ["date", "open","high", "low", "close", "volume", "tic"]
                i_df.date = i_df.date.apply(lambda d: datetime.fromtimestamp(d/1000))
                df = df.append(i_df)
                print(f"coin {i} completed...")
            except:
                print(f'coin {i} not available')
                pass
        print(df.shape)
        return df

    def select_equal_rows_stock(self, df,start_date: str, end_date: str, ticker_list: list):
        self.start_date = start_date
        self.end_date = end_date
        self.ticker_list = ticker_list
        df_check = df.tic.value_counts()
        df_check = pd.DataFrame(df_check).reset_index()
        df_check.columns = ["tic", "counts"]
        mean_df = df_check.counts.mean()
        equal_list = list(df.tic.value_counts() >= mean_df)
        names = df.tic.value_counts().index
        select_stocks_list = list(names[equal_list])
        df = df[df.tic.isin(select_stocks_list)]
        return df

 
