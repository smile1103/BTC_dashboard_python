class Watchlist:
    def __init__(self , pd , st , client):
        self.pd = pd
        self.st = st
        self.client = client
        self.watchlist_current = pd.read_csv("watchlist.csv").iloc[:, 1].to_list()# load current  watchlist from CSV
    def content_watchlist(self):
        # pull all tickers from Binance and select all USDT pairs
        tickers_all = self.pd.DataFrame(data = self.client.get_all_tickers())["symbol"]
        tickers_usdt = []
        for i in range(len(tickers_all)):
            if "USDT" in tickers_all[i]:
                tickers_usdt.append(tickers_all[i])

        # sort tickers alphabetically
        tickers_usdt = sorted(tickers_usdt)
        print(type(tickers_usdt))

        # search filter
        ticker_search = self.st.text_input(label = "Suche").upper()

        ticker_results = []
        for ticker in tickers_usdt:
            if ticker_search in ticker:
                ticker_results.append(ticker)
        if ticker_search != "":
            tickers_usdt = ticker_results + self.watchlist_current

        # add or remove tickers from watchlist via multiselect form
        with self.st.form(key = "Watchlist"):
            watchlist_test = self.st.multiselect(label = "Auswahl Watchlist", 
                                                 options = tickers_usdt, 
                                                 default = self.watchlist_current)
            submit_button = self.st.form_submit_button(label = "Bestätigen")
        if submit_button:
            watchlist_df = self.pd.DataFrame(watchlist_test)

            # save new watchlist as CSV
            watchlist_df.to_csv("watchlist.csv")