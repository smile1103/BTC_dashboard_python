import charts_module
class Sentiment:
    def __init__(self , st , requests , pd ,timedelta , go , client , sb1 ,make_subplots , ct , Client):
        self.st = st
        self.requests = requests
        self.pd = pd
        self.timedelta = timedelta
        self.go = go
        self.client = client
        self.sb1 = sb1
        self.make_subplots = make_subplots
        self.ct = ct
        self.Client = Client
    def go_figure(self , fg_index ,fg_index_value , fg_text ,go):
        self.fg_x = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = fg_index["value"][len(fg_index["value"])-fg_index_value],
        title = {'text': f"Vor einem Monat: {fg_text}"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {'axis': {'range': [0, 100]},
                'bar': {'color': '#1c1c1c'},
                'steps' : [{'range': [0, 25], 'color': "rgba(219, 7, 0, 0.8)"},
                            {'range': [25, 50], 'color': "rgba(219, 142, 0, 0.9)"},
                            {'range': [50, 75], 'color': "rgba(219, 212, 0, 0.9)"},
                            {'range': [75, 100], 'color': "rgba(0, 219, 7, 0.8)"}]}))
    def sentiment_content(self):
        st = self.st
        requests = self.requests
        pd = self.pd
        timedelta = self.timedelta
        go = self.go
        client = self.client
        sb1 = self.sb1
        make_subplots = self.make_subplots
        ct = self.ct
        Client = self.Client

        st.subheader("Bitcoin Angst und Gier Index")
        

        # Daten ziehen via Requests
        response_fg_index = requests.get("https://api.alternative.me/fng/?limit=0")
        
        # Datenaufbereitung
        fg_index = pd.json_normalize(response_fg_index.json()["data"])
        fg_updatetime = timedelta(seconds = int(fg_index["time_until_update"][0]))
        fg_index["timestamp"] = pd.to_datetime(fg_index["timestamp"], unit = "s")
        fg_currentdate = fg_index["timestamp"][0]
        fg_index = fg_index.iloc[::-1]
        fg_index.set_index(fg_index["timestamp"], inplace = True)
        fg_index.drop(['timestamp'], axis = 1, inplace = True)
        fg_index["value"] = fg_index["value"].astype(int)
        
        val_class_now = fg_index["value_classification"][len(fg_index["value"])-1]
        val_class_yest = fg_index["value_classification"][len(fg_index["value"])-2]
        val_class_week = fg_index["value_classification"][len(fg_index["value"])-8]
        val_class_month = fg_index["value_classification"][len(fg_index["value"])-31]

        
        ########
        ### Bitcoin F&G Indikatoren
        symbol = sb1.symbol_select
        # Index Indicator Aktuell
        self.go_figure(fg_index , 1 , val_class_now , go)
        fg_indicator1 = self.fg_x
        

        fg_indicator1.update_layout(margin = dict(l=30, r=30, t=30, b=0), width = 300, height = 200)

        # Index Indicator Gestern
        self.go_figure(fg_index , 2 , val_class_yest , go)
        fg_indicator2 = self.fg_x
        fg_indicator2.update_layout(margin = dict(l=30, r=30, t=30, b=0), width = 300, height = 200)

        # Index Indicator vor einer Woche
        self.go_figure(fg_index , 8 , val_class_week , go)
        fg_indicator3 = self.fg_x
        fg_indicator3.update_layout(margin = dict(l=30, r=30, t=30, b=0), width = 300, height = 200)

        # Index Indicator vor einem Monat
        self.go_figure(fg_index , 31 , val_class_month , go)
        fg_indicator4 = self.fg_x
        fg_indicator4.update_layout(margin = dict(l=30, r=30, t=30, b=0), width = 300, height = 200)

        st.text(f"letztes Datum: {fg_currentdate}, Zeit bis Update: {fg_updatetime}")

        fgcol1, fgcol2, fgcol3, fgcol4 = st.columns([1, 1, 1, 1])

        with fgcol1:
            st.plotly_chart(fg_indicator1)
        
        with fgcol2:
            st.plotly_chart(fg_indicator2)
        
        with fgcol3:
            st.plotly_chart(fg_indicator3)

        with fgcol4:
            st.plotly_chart(fg_indicator4)

        ########
        ### Bitcoin F&G Chart

        sb1.period_select = st.slider(label = "Anzahl Kerzen", 
                                min_value = 200, 
                                max_value = 2000, 
                                value = 500, 
                                step = 100)

        if sb1.period_select >= len(fg_index["value"]):
            sb1.period_select = len(fg_index["value"])
        
        # Ziehen der historischen Daten mit python-binance Library und Speichern in Data Frame
        data = pd.DataFrame(data = client.get_historical_klines(symbol = f"{symbol}USDT", interval = Client.KLINE_INTERVAL_1DAY, start_str = f"{sb1.period_select} days ago UTC"), 
                            columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Volume', 'Number of Trades', 'Taker buy Volume', 'Taker buy Quote', 'Ignore'])

        # Datenaufbereitung
        data = data.astype(float)
        data["Time"] = pd.to_datetime(data["Time"], unit = "ms")

        ########
        ### Chart plotten
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])                             
        
        ct.fig_add_trace(fig , go , data , symbol)
        fig = ct.fig_x

        # F&G plotten
        fig.add_trace(go.Scatter(x = data['Time'],
                                    y = fg_index["value"].tail(sb1.period_select),
                                    name = "Angst und Gier Index",
                                    opacity = 0.5,
                                    line=dict(color = "#4a7aff")),
                                    secondary_y = True)

        ##########
        ##### Anpassen des F&G Charts

        ct.fig_update_trace(fig , sb1)
        fig = ct.fig_x

        # Mausradzoom, Werkzeugleiste
        config = dict({'scrollZoom': True, 'displayModeBar': True})

        st.plotly_chart(fig, config = config)

        ########################
        ### Google Suchinteresse
        
        with st.expander("Google Suchinteresse", expanded = False):
            
            st.subheader("Google Suchinteresse")