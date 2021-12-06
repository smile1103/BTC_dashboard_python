################
### requirements
################

# streamlit (app construction)
import streamlit as st

# data acquisition
import requests
import config
from binance.client import Client
client = Client(config.API_KEY, config.API_SECRET)
from pytrends.request import TrendReq

# data handling
import pandas as pd
import numpy as np
from datetime import timedelta

# data analysis
from ta.trend import EMAIndicator, SMAIndicator, IchimokuIndicator
from ta.volume import ForceIndexIndicator
from ta.volatility import bollinger_hband, bollinger_lband

# using R within Python
from rpy2 import robjects
import warnings
from rpy2.rinterface import RRuntimeWarning
warnings.filterwarnings('ignore', category = FutureWarning)
warnings.filterwarnings('ignore', category = RRuntimeWarning)
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import StrVector
from rpy2.robjects import pandas2ri
pandas2ri.activate()
base = importr('base')
utils = importr('utils')
utils.chooseCRANmirror(ind=1)
utils.install_packages(StrVector('MultipleBubbles'))
bubble = importr('MultipleBubbles')

# plotting
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#component modules
import sidebar_module
import watchlist_module
import overview_module
import charts_module
import sentiment_module

#########################
### streamlit main layout
#########################

#######################
# titel and layout mode
st.set_page_config(page_title = "Krypto Analysetool", layout = "wide")

#########
# sidebar

sb1 = sidebar_module.Sidebar(st , pd)
sb1.show_sidebar()
option = sb1.option

########################
### wachtlist management
########################

wl1 = watchlist_module.Watchlist(pd , st , client)

##################################
# load current  watchlist from CSV
watchlist = wl1.watchlist_current

##################
# update watchlist
if option == "Watchlist":
    wl1.content_watchlist()

####################
### overview desktop
####################

if option == 'Überblick':
    ov1 = overview_module.Overview(st , pd , watchlist , client , go , Client , TrendReq , requests)
    ov1.coininfo_content()
    
##################
### charts desktop
##################

if option == 'Charts':
    ct = charts_module.Charts(st , sb1 , pd , go , client , Client , make_subplots , EMAIndicator , ForceIndexIndicator , robjects , np , SMAIndicator , IchimokuIndicator , timedelta , bollinger_hband , bollinger_lband )
    ct.charts_content()
    
#####################
### Sentiment Desktop
#####################

if option == 'Sentiment':
    ct = charts_module.Charts(st , sb1 , pd , go , client , Client , make_subplots , EMAIndicator , ForceIndexIndicator , robjects , np , SMAIndicator , IchimokuIndicator , timedelta , bollinger_hband , bollinger_lband)
    ################################
    ### Bitcoin Fear and Greed Index
    senmt = sentiment_module.Sentiment(st , requests , pd , timedelta , go ,client , sb1 , make_subplots , ct , Client) 
    senmt.sentiment_content()
    
######################
### Stocktwits Desktop
######################

if option == 'Stocktwits Posts':
    
    # Daten von Stocktwits ziehen
    symbol = sb1.symbol_select
    r = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json")
    data = r.json()
    # Stocktwits Posts zu angegebenem Ticker darstellen
    for message in data['messages']:
        st.image(message['user']['avatar_url'])
        st.write(message['user']['username'])
        st.write(message['created_at'])
        st.write(message['body'])