class Sidebar:
    def __init__(self , st , pd):
        self.st = st
        self.pd = pd
        # show_sidebar(self.st , self.pd)
    def show_sidebar (self):
        self.st.sidebar.title("Krypto Analysetool")
        self.option = self.st.sidebar.selectbox(label = "Auswahl Desktop", 
                                           options = ('Überblick', 'Watchlist', 'Charts', 'Sentiment', 'Stocktwits Posts'), 
                                           index = 0)
        if self.option == "Charts" or self.option == "Sentiment" or self.option == "Stocktwits Posts":
            self.st.sidebar.header("Optionen")
            symbol_options =  [symbol.replace("USDT", "") for symbol in self.pd.read_csv("watchlist.csv").iloc[:, 1].to_list()]
            self.symbol_select = self.st.sidebar.selectbox(label = "Auswahl Kürzel", 
                                            options = ['Anderes'] + symbol_options, 
                                            index = 1)
            if self.symbol_select == 'Anderes':
                self.symbol_select = self.st.sidebar.text_input("Kryptowährung Kürzel Eingabe", value='BTC', max_chars=5, key=None, type='default')     
        if self.option == "Charts" or self.option == "Sentiment":
            # choose interval for charts and sentiment
            self.interval_select = self.st.sidebar.selectbox(label = "Interval", 
                                            options = ("15 Minuten", "1 Stunde", "1 Tag", "1 Woche"), 
                                            index = 2)
            # choose number of bars for charts and sentiment
            self.period_select = self.st.sidebar.slider(label = "Anzahl Kerzen", 
                                min_value = 50, 
                                max_value = 750, 
                                value = 300, 
                                step = 50)
        # choose indicator desktop for charts and sentiment
        if self.option == "Charts":
            self.chart_select = self.st.sidebar.selectbox(label = "Analyse Charts", 
                                        options = ("Volumen", "Zeitreihenprozess", "Trend", "Volatilität", "Pi-Cycle Indicator"), 
                                        index = 0)
        if self.option == "Charts" or self.option == "Sentiment":
            # show candle info for charts and sentiment
            cinfo = self.st.sidebar.checkbox("Kerzeninfo anzeigen", value = True)
            if cinfo == True:
                self.hdist = 1
            else:
                self.hdist = 0
            # enable logarithmic scale for charts and sentiment
            logy = self.st.sidebar.checkbox("logarithmische Darstellung", value = True)
            if logy == True:
                self.scale = "log"
            else:
                self.scale = "linear"