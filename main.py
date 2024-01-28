"""
Pranavan Krishnamoorthy
Dec 11 2023
StockTrack is an app that allows the user to enter a stock by its ticker
and get up to date information on its price. It displays the metrics via
graphs, and other stats such as the open, high, low, and closing price

Instuctions:
================================================================================
    1,Enter stock tickersymbol into search box, e.i AAPL(Apple), TSLA(Tesla),
    2.Adjust the time period and interval to your liking,
    3.Change the chart view. Note! if interval is low and time period is high the graph
      may not load,
    4.Set start and end date instead of time period. Note! range must be within 60 days
      days can't be non-trading days either(usually weekends)
================================================================================
"""

import tkinter as tk
import yfinance as yf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
import pandas as pd
from tkinter import ttk

# global colours
TOOLBAR = "SteelBlue4"
MAIN = "white smoke"
CHART_BG = "white"
SUB = "azure"
FG = "black"

# options for timeperiod and selected graph
time_periods ={0: "1d",1: "5d",2: "1mo",3: "6mo",4: "YTD",5: "1y",6:"5y",7: "max"}
chart_view  ={False: "line",True: "candle"}

class StockTrack:
    def __init__(self):
        self.main = tk.Tk()
        self.main.geometry("1200x600")
        self.main.title("StockTrack")
        self.main["bg"]= MAIN
# -------------------------------------------------------------------------
        # top frame holding the search bar
        self.toolbar = tk.Frame(bg=TOOLBAR,height=20)
        self.toolbar.pack(fill="x", ipadx=10)

        # self.title=tk.Label(self.toolbar,text="StockTrack",fg="white",bg=TOOLBAR,font=("Helvetica",22))
        # self.title.pack(side="left", padx=5)

        self.search_entry = tk.Entry(self.toolbar, width=30, bg="white", font=("Helvetica", 10), fg=FG)
        self.search_entry.pack(side="left", fill="y", pady=3, padx=(10, 0))

        icon = tk.PhotoImage(file = "searchImage.gif")
        icon = icon.subsample(23, 23)
        self.search_button = tk.Button(self.toolbar, image=icon, command=self.load_chart)
        self.search_button.pack(side="left", pady=3)

# -------------------------------------------------------------------------
        # the time frame holds the period selector of the graph, using a for loop to interate over a
        # range of buttons and a list to hold the text for the buttons saves space

        self.time_frame=tk.Frame(bg=SUB)
        self.time_frame.pack(anchor="n", pady=4)

        self.time_var= tk.IntVar()
        self.time_var.set(7) # initialize to MAX

        periods=["1D","5D","1M","6M","YTD","1Y","5Y","MAX"] # texts for the buttons
        for i in range(8):
            btn=tk.Radiobutton(self.time_frame, font=("Helvetica",10), text=periods[i],value=i, \
                                variable=self.time_var, command=self.load_chart, \
                                selectcolor=MAIN, bg=MAIN, fg=FG)
            btn.pack(side="left",padx=10)

# -------------------------------------------------------------------------
        self.info_frame = tk.Frame()
        self.info_frame.pack(expand=True, fill="x", anchor="n")

        self.stock_name = tk.StringVar()
        self.stock_price = tk.StringVar()
        self.currency = tk.StringVar()

        self.stock_name_label = tk.Label(self.info_frame, textvariable=self.stock_name, font=("Helvetica", 12))
        self.stock_price_label = tk.Label(self.info_frame, textvariable=self.stock_price, font=("Helvetica", 25), anchor="w")
        self.currency_label = tk.Label(self.info_frame, textvariable=self.currency, font=("Helvetica", 12))

        self.stock_name_label.grid(column=0, row=0)
        self.stock_price_label.grid(column=0, row=1, padx=10) # current price
        self.currency_label.grid(column=1, row=1)

# -------------------------------------------------------------------------
        self.chart_frame = tk.Frame(bg=CHART_BG)
        self.chart_frame.pack()
# -------------------------------------------------------------------------
        self.option_Frame = tk.Frame(bg=CHART_BG)
        self.option_Frame.pack(expand=True, fill="x", anchor="s")

        # change graph view mode
        self.is_candle_mode = tk.BooleanVar()
        self.is_candle_mode.set(False)
        self.set_candle = tk.Checkbutton(self.option_Frame, text="Candle View", variable=self.is_candle_mode, command=self.load_chart, bg=CHART_BG, fg=FG)
        self.set_candle.pack(side="left")

        self.interval = tk.Label(self.option_Frame, text="Interval")
        self.interval.pack(side="left", padx=(15, 2))
        self.interval_var = tk.StringVar()
        self.intervalchoosen = ttk.Combobox(self.option_Frame, width = 27, textvariable = self.interval_var)
        self.intervalchoosen.pack(side="left")


        # refresh the graph
        self.refresh_btn = tk.Button(self.option_Frame, bg=TOOLBAR, width=15, text="Refresh", fg="white", command=self.load_chart)
        self.refresh_btn.pack(fill="y",side="right", anchor="e")

        # specific date range entry boxes
        self.end_date = tk.Entry(self.option_Frame)
        self.end_date.pack(side="right")
        self.end_label = tk.Label(self.option_Frame, text="End: ").pack(side="right")
        self.start_date = tk.Entry(self.option_Frame)
        self.start_date.pack(side="right")
        self.start_label = tk.Label(self.option_Frame, text="Start: ").pack(side="right")


        # interval values for combobox
        self.intervalchoosen['values'] = ('1m','5m','15m','30m','60m','90m', \
                                '1h','1d','5d','1wk','1mo','3mo')

        self.interval_var.set("1d")
# -------------------------------------------------------------------------
        self.metric_frame=tk.Frame(bg="snow2")
        self.metric_frame.pack(fill="both")

        self.info_frame = tk.Frame(bg="snow2")
        self.info_frame.pack(side="left", fill="both", ipadx=10, ipady=10, expand=True)
        self.discription = tk.Frame(bg="snow2")
        self.discription.pack(side="right", expand=True, fill="both")

        labels = [["Open", "Mkt cap", "52wk high"],
                  ["High", "P/E ratio", "52wk low"],
                  ["Low", "Recommend", ""]]
        for i in range(3):
            for j in range(5):
                if j % 2 == 0:
                    info_label = tk.Label(self.info_frame, text=labels[i][j//2], font=("Helvetica", 12), bg="snow2")
                    info_label.grid(row=i,column=j, padx=20, pady=3)

        self.open_var = tk.StringVar()

        self.open_label = tk.Label(self.info_frame, textvariable=self.open_var, bg="snow2")
        self.open_label.grid(row=0,column=1)

        self.high_var = tk.StringVar()
        self.high_label = tk.Label(self.info_frame, textvariable=self.high_var, bg="snow2")
        self.high_label.grid(row=1,column=1)

        self.low_var = tk.StringVar()
        self.low_label = tk.Label(self.info_frame, textvariable=self.low_var, bg="snow2")
        self.low_label.grid(row=2,column=1)

        self.mktcap_var = tk.StringVar()
        self.mktcap_label = tk.Label(self.info_frame, textvariable=self.mktcap_var, bg="snow2")
        self.mktcap_label.grid(row=0,column=3)

        self.peratio_var = tk.StringVar()
        self.peratio_label = tk.Label(self.info_frame, textvariable=self.peratio_var, bg="snow2")
        self.peratio_label.grid(row=1,column=3)

        self.div_yield_var = tk.StringVar()
        self.div_yield_label = tk.Label(self.info_frame, textvariable=self.div_yield_var, bg="snow2")
        self.div_yield_label.grid(row=2,column=3)

        self.wk_high_var = tk.StringVar()
        self.wk_high_label = tk.Label(self.info_frame, textvariable=self.wk_high_var, bg="snow2")
        self.wk_high_label.grid(row=0,column=5)

        self.wk_low_var = tk.StringVar()
        self.wk_low_label = tk.Label(self.info_frame, textvariable=self.wk_low_var, bg="snow2")
        self.wk_low_label.grid(row=1,column=5)

        self.discription_var = tk.StringVar()
        self.discription_label = tk.Label(self.discription, textvariable=self.discription_var, bg="snow2",
                                          wraplength=self.discription.winfo_screenmmwidth() * 2)
        self.discription_label.pack(padx=10, pady=10)

        tk.mainloop()

    def set_info(self, corp, data, name, currency):
        # sets the dynamic label variabels to the stock information
        self.stock_name.set(name)
        self.currency.set(currency)

        if corp.get("currentPrice") != None:
             self.stock_price.set("%.2f" %corp["currentPrice"])
        else:
             self.stock_price.set("%.2f" %data["Close"].iloc[-1])

        self.open_var.set(corp["open"])
        self.high_var.set(corp["dayHigh"])
        self.low_var.set(corp["dayLow"])

        if corp.get("marketCap") != None:
                self.mktcap_var.set(corp["marketCap"])
        if corp.get("trailingPE") != None:
            self.peratio_var.set("%.2f" %corp.get("trailingPE") + "%")

        if corp.get("recommendationKey") != None:
            self.div_yield_var.set(corp["recommendationKey"])

        self.wk_high_var.set(corp["fiftyTwoWeekHigh"])
        self.wk_low_var.set(corp["fiftyTwoWeekLow"])

        if corp.get("longBusinessSummary") != None:
             self.discription_var.set(corp["longBusinessSummary"])
        else:
             self.discription_var.set(corp["description"])

    def get_data(self, ticker):
        ticker = self.search_entry.get()
        corp = yf.Ticker(ticker)
        if self.start_date.get() == "" and self.end_date.get() == "":
            pd_data = pd.DataFrame(corp.history(period=time_periods[self.time_var.get()], \
                                                interval=self.interval_var.get()))
        else:
            pd_data = pd.DataFrame(corp.history(start=self.start_date.get(), end=self.end_date.get(), \
                                            interval=self.interval_var.get()))
        return (corp, pd_data)

    def load_chart(self):
        # destroys any old graph so the new on doesnt overlap
        for i in self.chart_frame.winfo_children():
            i.destroy()

        ticker = self.search_entry.get()
        corp, pd_data = self.get_data(ticker)

        self.set_info(corp.info, pd_data, corp.info["shortName"], corp.info["currency"])

        # create the graph
        fig = mpf.figure(figsize=(15,5),style="yahoo")
        axlist = fig.add_axes([0.1,0.2,0.8,0.8])
        mpf.plot(pd_data, type=chart_view[self.is_candle_mode.get()],ax=axlist, tight_layout=True, linecolor="#34a32e", show_nontrading=False)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()

        # placing the canvas on the Tkinter window
        canvas.get_tk_widget().pack(expand=True, fill="both")

stockrtack = StockTrack()
