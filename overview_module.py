class Overview:
    def __init__(self , st , pd , watchlist , client ,go , Client , TrendReq , requests):
        self.st = st
        self.pd = pd
        self.watchlist = watchlist
        self.client = client
        self.go = go
        self.Client = Client
        self.TrendReq = TrendReq
        self.requests = requests
        # columns for headers
        colü_head1, colü_head2, colü_head3 = st.columns([1.65, 1, 1.5])
        # insert headers
        with colü_head1:
            st.header("Watchlist")
        with colü_head2:
            st.header("Sentiment")
        with colü_head3:
            st.header("News")
    ###########
    # coin info
    def coininfo_content(self):
        # columns for overview
        col1, col2, col3, col4, col5, col6 = self.st.columns([0.5, 0.35, 0.4, 0.4, 1, 1.5])
        # wachtlist symbols
        with col1:
            self.st.subheader("Ticker")
            for i in self.watchlist:
                self.st.subheader(i)
        # price for wachtlist symbols        
        with col2:
            self.st.subheader("Kurs")
            all_tickers = self.pd.DataFrame(data = self.client.get_all_tickers())
            all_tickers = all_tickers.set_index('symbol')
            for i in self.watchlist:
                self.st.subheader(round(number = float(all_tickers.loc[i]), ndigits = 4))
        # 24h change for wachtlist symbols
        with col3:
            self.st.subheader("24 Std. %")

            change = self.go.Figure()
            
            # add streamlit indicators
            for i in range(0, len(self.watchlist)):
                change.add_trace(self.go.Indicator(mode = "delta",
                                                value = float(list(self.client.get_ticker(symbol = self.watchlist[i]).values())[2])/100,
                                                delta = {'reference': 0, 'relative': False, 'valueformat': '.2%'},
                                                domain = {'row': i, 'column': 1}))
            
            change.update_layout(grid = {'rows': len(self.watchlist), 'columns': 1, 'pattern': "independent", 'ygap': 0.5},
                                    margin = dict(l = 1, r = 1, t = 5, b = 0),
                                    height = 51.3*len(self.watchlist))

            self.st.plotly_chart(change, use_container_width = True)

        # 7d change for wachtlist symbols
        with col4:
            self.st.subheader("7 Tage %")

            week_change = self.go.Figure()

            # price one week ago
            week_ago = []

            for i in self.watchlist:
                week_ago_symbol = self.pd.DataFrame(data = self.client.get_historical_klines(symbol = i, interval = self.Client.KLINE_INTERVAL_1DAY, start_str = "7 days ago UTC", end_str = "6 days ago UTC"), 
                                                columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Volume', 'Number of Trades', 'Taker buy Volume', 'Taker buy Quote', 'Ignore'])
                
                week_ago.append(week_ago_symbol['Open'])
        
            # add streamlit indicators
            for i in range(0, len(self.watchlist)):
                week_change.add_trace(self.go.Indicator(mode = "delta",
                                                    value = float(list(self.client.get_ticker(symbol = self.watchlist[i]).values())[5]),
                                                    delta = {'reference': float(week_ago[i]), 'relative': True, 'valueformat': '.2%'},
                                                    domain = {'row': i, 'column': 1}))
                
            week_change.update_layout(grid = {'rows': len(self.watchlist), 'columns': 1, 'pattern': "independent", 'ygap': 0.5},
                                    margin = dict(l = 1, r = 1, t = 5, b = 0),
                                    height = 51.3*len(self.watchlist))

            self.st.plotly_chart(week_change, use_container_width = True)

        # sentiment
        with col5:
            
            # Google search interest "Bitcoin"
            pytrend = self.TrendReq(hl='en-US', tz=360)
            pytrend.build_payload(kw_list = ['Bitcoin'], cat = 0, timeframe = 'today 5-y', geo = '', gprop = '')
            interest = pytrend.interest_over_time()
            interest = interest["Bitcoin"].tail(1)

            # add indicator
            googleSI = self.go.Figure(self.go.Indicator(
                mode = "gauge+number",
                value = interest[0],
                title = {'text': f"Google SI: Bitcoin"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {'axis': {'range': [0, 100]},
                        'bar': {'color': '#1c1c1c'},
                        'steps' : [{'range': [0, 25], 'color': "rgba(219, 7, 0, 0.7)"},
                                    {'range': [25, 50], 'color': "rgba(219, 142, 0, 0.8)"},
                                    {'range': [50, 75], 'color': "rgba(219, 212, 0, 0.8)"},
                                    {'range': [75, 100], 'color': "rgba(0, 219, 7, 0.7)"}]}))

            googleSI.update_layout(margin = dict(l=25, r=30, t=5, b=5), width = 300, height = 220)

            # Google search interest "How to buy Bitcoin"
            pytrend.build_payload(kw_list = ['how to buy Bitcoin'], cat = 0, timeframe = 'today 5-y', geo = '', gprop = '')
            interest2 = pytrend.interest_over_time()
            interest2 = interest2["how to buy Bitcoin"].tail(1)
            
            # add indicator
            googleSI2 = self.go.Figure(self.go.Indicator(
                mode = "gauge+number",
                value = interest2[0],
                title = {'text': f"Google SI: How to buy Bitcoin"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {'axis': {'range': [0, 100]},
                        'bar': {'color': '#1c1c1c'},
                        'steps' : [{'range': [0, 25], 'color': "rgba(219, 7, 0, 0.8)"},
                                    {'range': [25, 50], 'color': "rgba(219, 142, 0, 0.9)"},
                                    {'range': [50, 75], 'color': "rgba(219, 212, 0, 0.9)"},
                                    {'range': [75, 100], 'color': "rgba(0, 219, 7, 0.8)"}]}))

            googleSI2.update_layout(margin = dict(l=25, r=30, t=5, b=5), width = 300, height = 220)

            # Bitcoin fear and greed index image
            self.st.image(image = "https://alternative.me/crypto/fear-and-greed-index.png", width = 280)
            # Google search interest indicators
            self.st.plotly_chart(googleSI)
            self.st.plotly_chart(googleSI2)

        # newsterminal
        with col6:
            
            # pull news from cryptopanic
            response_news = self.requests.get("https://cryptopanic.com/api/v1/posts/?auth_token=9c8938ad5c8ed752ce592beab257f9906f972ecb")
            news = self.pd.json_normalize(response_news.json()["results"])
            
            for i in range(len(news["title"])):
                self.st.write(news["title"][i])
                news_date = news["published_at"][i]
                news_source = news["source.domain"][i]
                self.st.caption(f"{news_date}, {news_source}")