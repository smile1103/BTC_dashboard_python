class Charts:
    def __init__(self , st , sb1 , pd , go , client , Client ,make_subplots , EMAIndicator , ForceIndexIndicator , robjects , np , SMAIndicator , IchimokuIndicator , timedelta , bollinger_hband , bollinger_lband):
        self.st = st
        self.sb1 = sb1
        self.pd = pd
        self.go = go
        self.client = client
        self.Client = Client
        self.make_subplots = make_subplots
        self.EMAIndicator = EMAIndicator
        self.ForceIndexIndicator = ForceIndexIndicator
        self.robjects = robjects
        self.np = np
        self.SMAIndicator = SMAIndicator
        self.IchimokuIndicator = IchimokuIndicator
        self.timedelta = timedelta
        self.bollinger_hband = bollinger_hband
        self.bollinger_lband = bollinger_lband
    def fig_add_trace(self , fig_x , go , data , symbol):
        fig_x.add_trace(go.Candlestick(x = data['Time'],
                                                open = data['Open'],
                                                high = data['High'],
                                                low = data['Low'],
                                                close = data['Close'],
                                                name = symbol, 
                                                increasing_fillcolor = "#24A06B",
                                                decreasing_fillcolor = "#CC2E3C",
                                                increasing_line_color = "#2EC886",
                                                decreasing_line_color = "#FF3A4C"),
                                                row = 1,
                                                col = 1)
        self.fig_x = fig_x
    def fig_update_trace(self , fig_x , sb1 ):
        fig_x.update_layout(height = 800, 
                                    width = 1400,
                                    margin = dict(l=10, r=10, t=10, b=10),
                                    showlegend = True, 
                                    xaxis_rangeslider_visible = False,
                                    xaxis = {'gridcolor': "#1f292f", 'spikesnap': 'cursor', 'spikecolor': "grey", 'spikethickness': 1, 'dtick': "M12"},
                                    xaxis2 = {'anchor': 'y', 'overlaying': 'x', 'side': 'top', 'showgrid': False},
                                    yaxis = {'type': sb1.scale, 'gridcolor': '#1f292f', 'spikesnap': 'cursor', 'spikecolor': "grey", 'spikethickness': 1},
                                    yaxis2 = {'showgrid': False, 'zerolinecolor': '#808080', 'gridcolor': '#808080'},
                                    yaxis_domain = [0, 0.94],
                                    dragmode = "pan", 
                                    hoverdistance = sb1.hdist,
                                    hovermode = 'x unified')
        self.fig_x = fig_x
    def charts_content(self):
        sb1 = self.sb1
        pd = self.pd
        go = self.go
        st = self.st
        make_subplots = self.make_subplots
        EMAIndicator = self.EMAIndicator
        ForceIndexIndicator = self.ForceIndexIndicator
        client = self.client
        Client = self.Client
        symbol = self.sb1.symbol_select
        robjects = self.robjects
        np = self.np
        SMAIndicator = self.SMAIndicator
        IchimokuIndicator = self.IchimokuIndicator
        timedelta = self.timedelta
        bollinger_hband = self.bollinger_hband
        bollinger_lband = self.bollinger_lband
        
        col1_2, col2_2, col3_2 = st.columns([4, 1, 4])
        

        # format interval and period input for binance API
        interval = None

        if sb1.interval_select == "15 Minuten":
            interval = Client.KLINE_INTERVAL_15MINUTE
        if sb1.interval_select == "1 Stunde":
            interval = Client.KLINE_INTERVAL_1HOUR
        if sb1.interval_select == "1 Tag":
            interval = Client.KLINE_INTERVAL_1DAY
        if sb1.interval_select == "1 Woche":
            interval = Client.KLINE_INTERVAL_1WEEK
        
        period = None
        if sb1.interval_select == "15 Minuten":
            period = f"{sb1.period_select*15} minutes ago UTC"
        if sb1.interval_select == "1 Stunde":
            period = f"{sb1.period_select} hours ago UTC"
        if sb1.interval_select == "1 Tag":
            period = f"{sb1.period_select} days ago UTC"
        if sb1.interval_select == "1 Woche":
            period = f"{sb1.period_select} weeks ago UTC"
        ##########
        ##### pull data from binance

        # historical data as dataframe
        data = pd.DataFrame(data = client.get_historical_klines(symbol = f"{symbol}USDT", interval = interval, start_str = period), 
                            columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Volume', 'Number of Trades', 'Taker buy Volume', 'Taker buy Quote', 'Ignore'])
        # data manipulation
        data = data.astype(float)
        data["Time"] = pd.to_datetime(data["Time"], unit = "ms")

        # add historical bitcoin data
        data_hist = pd.read_csv("btc_ohlcvm.csv", sep = ';')
        
        # data manipulation
        data_hist.drop(['Marketcap'], axis = 1, inplace = True)   
        data_hist["Time"] = pd.to_datetime(data_hist["Time"])
        data_hist.set_index('Time', inplace = True)
        data_hist.astype(float)

        # aggregate to weekly OHLC
        agg_dict = {'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'mean'}

        data_hist2 = data_hist.resample('W-Mon').agg(agg_dict)
        data_hist2.reset_index(level = 0, inplace = True)

        # select weekly or daily data missing from binance (28. April 2013 to 07. August 2017)
        
        if sb1.interval_select == "1 Woche" or sb1.interval_select == "1 Tag":
            if sb1.interval_select == "1 Woche":
                data_hist_missing = data_hist2.loc[1:366, :]
            if sb1.interval_select == "1 Tag":
                data_hist.reset_index(level = 0, inplace = True)
                data_hist_missing = data_hist.loc[1:2572, :]
            if symbol == "BTC":
                data_cut = data.iloc[:, 0:6]
                data_full = pd.concat([data_hist_missing, data_cut], ignore_index = True)
                if sb1.period_select >= len(data_full["Close"]):
                    sb1.period_select = len(data_full["Close"])
                data = data_full.tail(sb1.period_select)
                data["Index"] = range(0, sb1.period_select)
                data.set_index("Index", inplace = True)
            else: data_full = data
        ##########
        ##### create main chart

        # main chart (candlestick with volume)
        st.subheader(f"{symbol}/USDT (Binance)")

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        self.fig_add_trace(fig , go , data , symbol)
        fig = self.fig_x
        # color of volume bars
        colors = []
        close = list(data["Close"])

        for i in range(len(close)):
            if i != 0:
                if close[i] > close[i-1]:
                    colors.append("#24A06B")
                else:
                    colors.append("#CC2E3C")
            else:
                colors.append("#CC2E3C")
            
        # plot volume bars
        fig.add_trace(go.Bar(x = data['Time'], 
                                y = data['Volume'], 
                                marker=dict(color = colors), 
                                name = "Volumen", 
                                opacity = 0.40), 
                                secondary_y = True)
        ##########
        ##### adjust layout

        # yaxis2 maximum
        vol_df = data["Volume"]
        max_vol = max(vol_df)
        range_top = max_vol*4 

        # Höhe und Breite definieren, Rand verkleinern, Legende einblenden, Zeitauswahl Slider entfernen, X-Achse anpassen, X-Achse2 anpassen, Y-Achse anpassen, "Schieben" als Standardwerkzeug, Kerzeninfo anzeigen)
        self.fig_update_trace(fig , sb1)
        fig = self.fig_x

        # scrollzoom, toolbar
        config = dict({'scrollZoom': True, 'displayModeBar': True})

        # plot chart
        if sb1.chart_select == "Volumen":
            with st.expander("Volume", expanded = True):
                st.plotly_chart(fig, config = config)
        else:
            with st.expander("Volume Chart", expanded = False):
                st.plotly_chart(fig, config = config)

        ##########
        ##### indicator charts

        # volumen desktop
        if sb1.chart_select == "Volumen":
            
            ##########
            ##### create volume profile

            st.subheader(f"{symbol} Volumenprofil")
            
            col1_2, col2_2, col3_2 = st.columns([4, 1, 4])
            
            # chart options
            with col1_2:
                # choose bar size
                round_interval_select = st.selectbox(label = "Balken Intervall", 
                                                    options = ("0.0025", "0.005", "0.01", "0.05", "0.1","0.5", "1", "2", "5", "10" ,"50", "100", "250","500", "750","1000", "2000"), 
                                                    index = 15)
            
            data["Close_rd"] = (data["Close"] / float(round_interval_select)).astype(int)*float(round_interval_select)
            
            # cumulate volume
            volprof = data["Volume"].groupby(data["Close_rd"]).sum()

            volprof_data = {'Pricelevel': volprof.index, 'Volume': volprof}
            volprof_df = pd.DataFrame(data = volprof_data, columns = ['Pricelevel', 'Volume'])

            ##########
            ##### plot volume profile

            fig_two = make_subplots(specs=[[{"secondary_y": True}]])
            
            self.fig_add_trace(fig_two , go , data , symbol)
            fig_two = self.fig_x
            fig_two.add_trace(go.Bar(x = volprof_df["Volume"], 
                                        y = volprof_df["Pricelevel"], 
                                        name = "Volumenprofil", 
                                        opacity=0.20, 
                                        orientation = "h", 
                                        marker=dict(color = "#5ecfff")), 
                                        secondary_y = False)
            
            ##########
            ##### adjust layout

            # Höhe und Breite definieren, Rand verkleinern, Legende einblenden, Zeitauswahl Slider entfernen, X-Achse anpassen, X-Achse2 anpassen, Y-Achse anpassen, "Schieben" als Standardwerkzeug, Kerzeninfo anzeigen)
            self.fig_update_trace(fig_two , sb1)
            fig_two = self.fig_x

            # X-Achse2 für Volumenprofil verwenden
            fig_two.data[1].update(xaxis = 'x2')

            # Mausradzoom, Werkzeugleiste
            config = dict({'scrollZoom': True, 'displayModeBar': True})

            # Chart ausgeben
            st.plotly_chart(fig_two, config = config)

            ##########
            ##### Berechnen des relativen Volumens

            ## Relatives Volumen (gesamter Balken zu Moving Average)
            st.subheader(f"{symbol} relatives Volumen")
            
            # Einstellen der Vergleichsperiode
            ema_days_select = int(st.selectbox(label = "Vergleichsperioden (EMA)", 
                                                    options = ("7", "14", "21", "30", "50","100", "200"), 
                                                    index = 2))

            # relatives Volumen berechnen (EMA14)
            ema_vergleich = EMAIndicator(data["Volume"], ema_days_select).ema_indicator()
            ema_3 = EMAIndicator(data["Volume"], 1).ema_indicator()
            ema_diff = (ema_3-ema_vergleich)/(ema_3+ema_vergleich)
            
            ##########
            ##### Erstellen des relativen Volumen Charts

            fig_three = make_subplots(specs=[[{"secondary_y": True}]])                             
            
            self.fig_add_trace(fig_three , go , data , symbol)
            fig_three = self.fig_x

            # relatives Volumen plotten
            fig_three.add_trace(go.Scatter(x = data['Time'],
                                        y = ema_diff,
                                        name = "Rel. Volume",
                                        opacity=0.7,
                                        line=dict(color = "#4a7aff")),
                                        secondary_y = True)

            ##########
            ##### Anpassen des relativen Volumen Charts

            self.fig_update_trace(fig_three , sb1)
            fig_three = self.fig_x

            # Mausradzoom, Werkzeugleiste
            config = dict({'scrollZoom': True, 'displayModeBar': True})

            st.plotly_chart(fig_three, config = config)

            ##########
            ##### Erstellen des Force Indikator Charts

            st.subheader(f"{symbol} Force Indicator")

            force_13 = ForceIndexIndicator(close = data['Close'], volume = data['Volume'], window = 13).force_index()/data['Close']

            # Basischart
            fig_four = make_subplots(specs=[[{"secondary_y": True}]])                             
            
            self.fig_add_trace(fig_four , go , data , symbol)
            fig_four = self.fig_x

            # Force Indikator
            fig_four.add_trace(go.Scatter(x = data['Time'],
                                        y = force_13,
                                        name = "Force Index",
                                        opacity=0.4,
                                        line = dict(color = "#7aa9ff")),
                                        secondary_y = True)

            ##########
            ##### Anpassen des Force Indikator Charts

            self.fig_update_trace(fig_four , sb1)
            fig_four = self.fig_x

            st.plotly_chart(fig_four, config = config)


        # Zeitreihen Desktop                
        if sb1.chart_select == "Zeitreihenprozess":
            
            st.subheader(f"{sb1.scale} Zeitreihenprozess")

            ##########
            ##### Berechnen des Explosive Indicators durch Zugriff auf R

            gsadf = robjects.r['sadf_gsadf']

            data['log_Close'] = np.log(data['Close'])
            
            explosive = gsadf(y = robjects.FloatVector(data['log_Close']), adflag = 1, mflag = 1, IC = 1, parallel = False)

            explosive_py = robjects.conversion.rpy2py(explosive)[1]
            data['explosive'] = np.append(np.repeat(np.NAN, (len(data)-len(explosive_py))), explosive_py)

            st.text(f"Explosive Indicator: {round(data['explosive'][len(data['explosive'])-1], 4)}")

            ##########
            ##### Plotten des Explosive Indicators

            # Basischart
            fig_five = make_subplots(specs=[[{"secondary_y": True}]])                             
            
            self.fig_add_trace(fig_five , go , data , symbol)
            fig_five = self.fig_x

            # Explosive Indicator
            fig_five.add_trace(go.Scatter(x = data['Time'],
                                        y = data['explosive'],
                                        name = "Explosive Indicator",
                                        opacity=0.5,
                                        line = dict(color = "#00fbff")),
                                        secondary_y = True)

            ##########
            ##### Anpassen des Explosive Indicator Charts

            self.fig_update_trace(fig_five , sb1)
            fig_five = self.fig_x

            st.plotly_chart(fig_five, config = config)
        
        # Trend Desktop
        if sb1.chart_select == "Trend":

            ##########
            ##### Moving Average Bands Chart

            st.subheader(f"{symbol} Trend Indicators")

            # Auswahl Indikatoren
            trend_indicators = st.multiselect(label = "Auswahl Trendindikatoren", 
                                                options = ["EMA 8", "EMA 50", "Bullmarket Supportband", "Accumulation Band", "Kijun-sen"], 
                                                default = ["Bullmarket Supportband", "Accumulation Band"])

            # Basischart
            fig_six = make_subplots(specs=[[{"secondary_y": False}]])                             
            
            self.fig_add_trace(fig_six , go , data , symbol)
            fig_six = self.fig_x

            # Bullmarket Supportband
            if "Bullmarket Supportband" in trend_indicators:    
                fig_six.add_trace(go.Scatter(x = data['Time'],
                                            y = EMAIndicator(data_full['Close'], 21).ema_indicator().tail(sb1.period_select),
                                            name = "Supportband",
                                            opacity = 0.8,
                                            line = dict(color = "#00c95b")))

                fig_six.add_trace(go.Scatter(x = data['Time'],
                                    y = SMAIndicator(data_full['Close'], 20).sma_indicator().tail(sb1.period_select),
                                    name = "Bullmarket",
                                    opacity = 0.8,
                                    line = dict(color = "#e39400"),
                                    fill = 'tonexty',
                                    fillcolor = "rgba(171, 171, 171, 0.15)"))

            # EMA 8
            if "EMA 8" in trend_indicators:
                fig_six.add_trace(go.Scatter(x = data['Time'],
                                    y = data_full['Close'].ewm(span = 8, adjust = False).mean().tail(sb1.period_select),
                                    name = "EMA 8",
                                    opacity = 0.8,
                                    line = dict(color = "#ffffff")))

            # EMA 50
            if "EMA 50" in trend_indicators: 
                fig_six.add_trace(go.Scatter(x = data['Time'],
                            y = data_full['Close'].ewm(span = 50, adjust = False).mean().tail(sb1.period_select),
                            name = "EMA 50",
                            opacity = 0.8,
                            line = dict(color = "#475dff")))

            # Accumulationband
            if "Accumulation Band" in trend_indicators:    
                fig_six.add_trace(go.Scatter(x = data['Time'],
                                            y = data_full['Close'].ewm(span = 200, adjust = False).mean().tail(sb1.period_select),
                                            name = "Band",
                                            opacity = 0.8,
                                            line = dict(color = "#5be300")))

                fig_six.add_trace(go.Scatter(x = data['Time'],
                                    y = data_full['Close'].ewm(span = 300, adjust = False).mean().tail(sb1.period_select),
                                    name = "Time",
                                    opacity = 0.8,
                                    line = dict(color = "#11c900"),
                                    fill = 'tonexty',
                                    fillcolor = "rgba(171, 171, 171, 0.1)"))

                fig_six.add_trace(go.Scatter(x = data['Time'],
                            y = data_full['Close'].ewm(span = 400, adjust = False).mean().tail(sb1.period_select),
                            name = "Accumulation",
                            opacity = 0.8,
                            line = dict(color = "#00a61c"),
                            fill = 'tonexty',
                            fillcolor = "rgba(171, 171, 171, 0.1)"))
            
            if "Kijun-sen" in trend_indicators:
                fig_six.add_trace(go.Scatter(x = data['Time'],
                            y = IchimokuIndicator(data_full['High'], data_full['Low'], 9, 26, 52).ichimoku_base_line().tail(sb1.period_select),
                            name = "Kijun-sen",
                            opacity = 0.8,
                            line = dict(color = "#ffdd00")))


            ##########
            ##### Anpassen des Moving Average Bands Charts

            self.fig_update_trace(fig_six , sb1)
            fig_six = self.fig_x

            st.plotly_chart(fig_six, config = config)
        
            ##########
            ##### Logarithmic Regression Bands Chart
            if symbol == "BTC":
                
                st.subheader(f"{symbol} Logarithmic Regression Rainbow")

                # Basischart
                fig_seven = make_subplots(specs=[[{"secondary_y": False}]])                        
                
                self.fig_add_trace(fig_seven , go , data , symbol)
                fig_seven = self.fig_x


                popt = [4.99, -22.7]

                # Predict with Logarithmic Regression
                logpred_x2 = pd.date_range(start = "2010-08-01", periods = (len(data_full["Close"])+150), freq = 'W-Mon')[-(sb1.period_select+150):] - timedelta(weeks = 47)
                logpred_start = (len(data_full["Close"])+150+1-(sb1.period_select+150))
                logpred_end = (len(data_full["Close"])+150+1)
                logpred_x = np.log(list(range(logpred_start, logpred_end)))

                # Regression Bands Fillcolors
                reg_fillcol = list(["rgba(255, 0 , 0, 0.1)", "rgba(255, 64, 0, 0.1)", "rgba(255, 127, 0, 0.1)", "rgba(255, 255, 0, 0.1)", 
                                    "rgba(0, 255, 0, 0.1)", "rgba(0, 191, 32, 0.1)", "rgba(0, 168, 109, 0.1)", "rgba(0, 0, 255, 0.1)"])
                reg_shift = [x*0.5+0.5 for x in range(6, -3, -1)][-8:]
                print(reg_shift)

                fig_seven.add_trace(go.Scatter(x = logpred_x2,
                                y = np.exp(popt[0]*logpred_x + popt[1] + 3.5),
                                name = "Log. Band",
                                opacity = 0.05,
                                xaxis = 'x1',
                                line = dict(color = "#808080", width = 1)))

                for i in range(0, 8):
                    fig_seven.add_trace(go.Scatter(x = logpred_x2,
                                            y = (np.exp(popt[0]*logpred_x + popt[1] + reg_shift[i])),
                                            name = f"Log. Band {str(i+1)}",
                                            opacity = 0.1,
                                            xaxis = 'x1',
                                            line = dict(color = "#808080", width = 1),
                                            fill = 'tonexty',
                                            fillcolor = reg_fillcol[i]))

                ##########
                ##### Anpassen des Logarithmic Regression Bands Charts

                self.fig_update_trace(fig_seven , sb1)
                fig_seven = self.fig_x
                st.plotly_chart(fig_seven, config = config)


            ##########
            ##### Logarithmic Regression Top and Bottom

            if symbol == "BTC":

                st.subheader(f"{symbol} Logarithmic Regression Top and Bottom")

                # Basischart
                fig_eight = make_subplots(specs=[[{"secondary_y": False}]])                        
                
                self.fig_add_trace(fig_eight , go , data , symbol)
                fig_eight = self.fig_x


                # Predict with Logarithmic Regression
                logpred_x2 = pd.date_range(start = "2010-08-01", periods = (len(data_full["Close"])+150), freq = 'W-Mon')[-(sb1.period_select+150):] - timedelta(weeks = 47)
                logpred_start = (len(data_full["Close"])+150+1-(sb1.period_select+150))
                logpred_end = (len(data_full["Close"])+150+1)
                logpred_x = np.log(list(range(logpred_start, logpred_end)))

                ##########
                ##### Logarithmic Regression Bottom Band
                
                popt_2 = [4.99, -22.7]

                # Upper Bound
                fig_eight.add_trace(go.Scatter(x = logpred_x2,
                y = np.exp(popt_2[0]*logpred_x + popt_2[1] + 0.5),
                name = "Upper Bottom Band",
                opacity = 0.5,
                xaxis = 'x1',
                line = dict(color = "rgba(0, 166, 28, 0.6)", width = 1)))
                
                # Main Regression
                fig_eight.add_trace(go.Scatter(x = logpred_x2,
                        y = np.exp(popt_2[0]*logpred_x + popt_2[1]),
                        name = "Main Bottom Band",
                        xaxis = 'x1',
                        line = dict(color = "rgba(17, 201, 0, 0.6)", width = 1.5),
                        fill = 'tonexty',
                        fillcolor = "rgba(17, 201, 0, 0.03)"))

                # Lower Bound
                fig_eight.add_trace(go.Scatter(x = logpred_x2,
                y = np.exp(popt_2[0]*logpred_x + popt_2[1] - 0.5),
                name = "Lower Bottom Band",
                opacity = 0.5,
                xaxis = 'x1',
                line = dict(color = "rgba(0, 166, 28, 0.6)", width = 1),
                fill = 'tonexty',
                fillcolor = "rgba(17, 201, 0, 0.03)"))

                ##########
                ##### Logarithmic Regression Top Band

                popt_3 = [4.7, -18.5]
                
                # Upper Regression
                fig_eight.add_trace(go.Scatter(x = logpred_x2,
                        y = np.exp(popt_3[0]*logpred_x + popt_3[1] + 0.25),
                        name = "Upper Top Band",
                        xaxis = 'x1',
                        line = dict(color = "rgba(255, 30, 0, 0.3)", width = 1)))

                # Main Regression
                fig_eight.add_trace(go.Scatter(x = logpred_x2,
                        y = np.exp(popt_3[0]*logpred_x + popt_3[1]),
                        name = "Main Top Band",
                        xaxis = 'x1',
                        line = dict(color = "rgba(255, 30, 0, 0.5)", width = 1.5),
                        fill = 'tonexty',
                        fillcolor = "rgba(255, 70, 46, 0.05)"))
                
                # Lower Regression
                fig_eight.add_trace(go.Scatter(x = logpred_x2,
                        y = np.exp(popt_3[0]*logpred_x + popt_3[1] - 0.25),
                        name = "Lower Top Band",
                        xaxis = 'x1',
                        line = dict(color = "rgba(255, 30, 0, 0.3)", width = 1),
                        fill = 'tonexty',
                        fillcolor = "rgba(255, 70, 46, 0.05)"))

                ##########
                ##### Anpassen des Logarithmic Regression Bands Charts

                self.fig_update_trace(fig_eight , sb1)
                fig_eight = self.fig_x

                st.plotly_chart(fig_eight, config = config)
        
        # Volatilität Desktop
        if sb1.chart_select == "Volatilität":

            st.subheader(f"{symbol} Bollinger Bands")

            # Basischart
            fig_nine = make_subplots(specs=[[{"secondary_y": False}]])
            self.fig_add_trace(fig_nine , go , data , symbol)
            fig_nine = self.fig_x
            fig_nine.add_trace(go.Scatter(x = data['Time'],
                                y = bollinger_hband(data["Close"], window = 20, window_dev = 2),
                                name = "Upper Band",
                                opacity = 0.8,
                                line = dict(color = "#11c900")))

            fig_nine.add_trace(go.Scatter(x = data['Time'],
                                y = bollinger_lband(data["Close"], window = 20, window_dev = 2),
                                name = "Lower Band",
                                opacity = 0.8,
                                line = dict(color = "#fc2003"),
                                fill = 'tonexty',
                                fillcolor = "rgba(171, 171, 171, 0.05)"))
        
            ##########
            ##### Anpassen des Bollinger Bands Charts

            self.fig_update_trace(fig_nine , sb1)
            fig_nine = self.fig_x
        
            st.plotly_chart(fig_nine, config = config)

        # Pi-Cycle Indicator Desktop
        if sb1.chart_select == "Pi-Cycle Indicator":

            if symbol == "BTC":

                st.subheader(f"{symbol} Pi-Cycle Indicator")

                pi_indicators = st.multiselect(label = "Auswahl Trendindikatoren", 
                                        options = ["Pi-Cycle Top Bands", "Pi-Cycle Bottom Bands"], 
                                        default = [])

                # Basischart
                fig_ten = make_subplots(specs=[[{"secondary_y": False}]])                        
                self.fig_add_trace(fig_ten , go , data , symbol)
                fig_ten = self.fig_x

                ##########
                ##### Pi-Cycle Top Indicator
                
                sma350_2 = (SMAIndicator(data_full['Close'], 350).sma_indicator().tail(sb1.period_select))*2
                sma111 = SMAIndicator(data_full['Close'], 111).sma_indicator().tail(sb1.period_select)

                # Locate Pi-Top
                picross = [l>=s for (l, s) in zip(sma350_2, sma111)]
                # Zeitreihe um eins nach Vorn verschieben
                picross_shift1 = [picross[1]]
                picross_shift1[1:] = picross[0:(len(sma350_2)-1)]
                # Abfragen ob der vorherige Wert gleich dem aktuellen ist und der vorherige Wert 
                picross = [x!=y & y == False for (x, y) in zip(picross, picross_shift1)]
                pitop = np.where(picross)

                print(pitop)

                if "Pi-Cycle Top Bands" in pi_indicators:
                    fig_ten.add_trace(go.Scatter(x = data['Time'],
                                y = sma350_2,
                                name = "SMA 350*2",
                                opacity = 0.8,
                                line = dict(color = "#d547f5")))
                
                    fig_ten.add_trace(go.Scatter(x = data['Time'],
                                y = sma111,
                                name = "SMA 111",
                                opacity = 0.8,
                                line = dict(color = "#47ecf5")))
                
                ##########
                ##### Pi-Cycle Bottom Indicator
                
                sma471_0745 = (SMAIndicator(data_full['Close'], 471).sma_indicator().tail(sb1.period_select))*0.745
                ema150 = EMAIndicator(data_full['Close'], 150).ema_indicator().tail(sb1.period_select)

                # add_vline

                if "Pi-Cycle Bottom Bands" in pi_indicators:
                    fig_ten.add_trace(go.Scatter(x = data['Time'],
                                y = sma471_0745,
                                name = "SMA 471*0745",
                                opacity = 0.8,
                                line = dict(color = "#d547f5")))
                
                    fig_ten.add_trace(go.Scatter(x = data['Time'],
                                y = ema150,
                                name = "EMA 150",
                                opacity = 0.8,
                                line = dict(color = "#47ecf5")))

                ##########
                ##### Anpassen des Pi-Cycle Indicator Charts

                self.fig_update_trace(fig_ten , sb1)
                fig_ten = self.fig_x
                        
                st.plotly_chart(fig_ten, config = config)
            
            else:
                st.subheader("Pi-Cycle Indikator ist nur für Bitcoin Verfügbar")