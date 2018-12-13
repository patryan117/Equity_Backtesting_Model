from collections import Counter
import pandas as pd
import os
import time
import numpy as np
import plotly
import plotly.offline
import plotly.graph_objs as go
import os

class backtest():

    def __init__ (self, strategy=1, index_name="XBI"):

        self.strategy = strategy
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.investment = 100
        self.strategy_name = "Strategy" + str(self.strategy)
        self.k_tup = [0, 0.25, 0.5, 0.75,  1, 1.25,  1.5, 1.75,  2, 2.25,  2.5, 2.75,  3]
        self.w_tup = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]   # trailing_sd window
        # self.k_tup = [0,  1,  2,  3]
        # self.w_tup = [10, 11, 12, 13, 14, 15 ]  # trailing_sd window
        self.transaction_cost = 0.25
        self.index_name = index_name
        self.index_df = self.get_transformed_index_data()

        self.micro_cap_list = ["ALDX", "BLRX", "KDMN", "KALV", "KMDA",  "PTGX",  "TRVN", "CDTX",  "MTNB", "NBRV", \
                               "KIN", "XOMA", "CMRX", "CTRV", "NNVC", "CDXS", "PFNX", "ATNM", "AGLE", "AFMD", \
                              "ALRN", "AVEO", "BTAI",  "FBIO", "GALT", "GNPX", "GTXI", "IMDZ", "IMGN", "IMMP",\
                               "INFI", "KURA", "LPTX", "MEIP",  "NK", "ONS", "PIRS", "RNN", "SLS", "SRNE", "STML",\
                               "SNSS", "TRIL", "VBLT", "VSTM",   "ZYME", "ZYNE", "AXSM", "NTEC", "NERV",  "TENX", \
                               "KRYS", "MNKD", "NEPT", "ADVM", "AGTC", "IMMY", "OCUL", "OHRP", "OPHT",  "OVAS",\
                               "RDHL", "PLX", "GNMX", "GEMP", "SELB", "CALA", "ADMA", "ASNS", "CFRX", "DVAX", \
                               "SMMT", "MTFB", "SPRO", "AMPE", "ABUS", "CNAT", "DRNA", "GLMD", "VTL", "ALNA", \
                              "CPRX", "CHMA", "EIGR", "FATE", "NVLN", "RGLS", "RCKT", "SBBP",  "XENE", "ATHX",
                              "PRQR", "PULM", "VRNA", "ARCT", "GLYC", "NYMX", "SPHS", "URGN", "GNCA", "SBPH", \
                              "VVUS", "ZFGN", "OBSV"]

        self.stock_return_dict = self.get_empty_stock_dict()
        self.stock_transaction_count_dict = self.get_empty_stock_dict()


        self.strategy_output = self.generate_net_return_spread()



    def print_index_df(self):
        print(self.index_df)


    def get_empty_stock_dict(self):
        dict = {}
        for x in self.micro_cap_list:
            dict[x] = 0
        return dict

    def plot_top_net_stock_returns(self, n=15):

        top_dict = dict(Counter(self.stock_return_dict).most_common(n))
        keys, values = zip(*top_dict.items())

        data = [go.Bar(
            x=list(values),
            y=list(keys),
            orientation='h'
        )]

        layout = go.Layout(title=str(
            "Top " + str(n) +  " Returns By Stock (" + "Strategy " + str(self.strategy) + ", Index = " + self.index_name + ", Transaction Cost = $" + str(
                self.transaction_cost) + ")",
        ),
            xaxis=dict(
                title='Net-Return'
            ),
            yaxis=dict(
                title='Stock Name'
            ),




                           )

        plotly.offline.plot({"data": data, "layout": layout})
        time.sleep(1)

    def plot_top_average_stock_returns(self, n=15):

        return_dict = self.stock_return_dict
        freq_dict = self.stock_transaction_count_dict
        average_return_dict = {}

        for key in return_dict:
            average_return_dict[key] = return_dict[key] / freq_dict[key]


        top_dict = dict(Counter(average_return_dict).most_common(n))
        keys, values = zip(*top_dict.items())

        def add_spaces(mylist):
            mylist= list(mylist)
            outlist = []
            for x in mylist:
                outlist.append(x + "  ")
            return outlist

        keys = add_spaces(keys)

        data = [go.Bar(
            x=list(values),
            y=list(keys),
            orientation='h'
        )]


        layout = go.Layout(title=str(
            "Top " + str(n) +  " Stocks by Average Net-Return (" + "Strategy " + str(self.strategy) + ", Index = " + self.index_name + ", Transaction Cost = $" + str(
                self.transaction_cost) + ")",
        ),
            xaxis=dict(
                title='Average Net-Return per Transaction (USD or % Gain)'
            ),
            yaxis=dict(
                title='Stock Name'
            ),
                           )

        plotly.offline.plot({"data": data, "layout": layout})
        time.sleep(1)

    def generate_net_return_spread(self):

        combo_list = (self.generate_cartesian_product(self.w_tup, self.k_tup))
        counter = 0
        w_list = []
        k_list = []
        net_return_list = []

        # index_df creation line should be here, so it doesnt need to be created for each investment simulation
        for i in combo_list:
            counter += 1
            cur_w = i[0]
            cur_k = i[1]
            net_return = self.calc_cum_return(cur_w, cur_k)
            w_list.append(cur_w)
            k_list.append(cur_k)
            net_return_list.append(net_return)

            print("****************************************", len(combo_list) - counter,
                  "Calculations Remaining ****************************************\n")

        return [tuple(w_list), tuple(k_list), tuple(net_return_list)]


    def plot_net_return_scatterplot(self):

        std_trailing_window = self.strategy_output[0]
        std_threshold = self.strategy_output[1]
        net_returns = self.strategy_output[2]

        scaled_net_returns = []  # scale down return
        minmax_return = max(max(net_returns), abs(min(net_returns)))

        for x in net_returns:
            y = x / minmax_return
            scaled_net_returns.append(abs(y) * 30)

        max_val = max(max(net_returns), abs(min(net_returns)))

        trace0 = go.Scatter(
            x=std_trailing_window,
            y=std_threshold,
            text=net_returns,
            mode='markers',
            marker=dict(
                color=net_returns,
                size=scaled_net_returns,
                showscale=True,
                cmax=max_val,
                cmin=(-max_val),
            )
        )

        data = [trace0]

        layout = go.Layout(title=str(
            "Net-Return Spread (" + "Strategy " + str(self.strategy) + ", Index = " + self.index_name + ", Transaction Cost = $" + str(
                self.transaction_cost) + ")"),
                           xaxis=dict(title='Trailing Calculation Window'),
                           yaxis=dict(title='σ Threshold'),
                           hovermode='closest'
                           )
        plotly.offline.plot({"data": data, "layout": layout})
        time.sleep(1)



    def plot_net_return_histogram(self, bins=15):

        x = self.strategy_output[2]
        data = [go.Histogram(x=x, histnorm='probability', nbinsx = bins,)]

        layout = go.Layout(
            title=("Net-Return Histogram (" + "Strategy " + str(self.strategy) + ", Index = " + self.index_name + ", Transaction Cost = $" + str(
                self.transaction_cost) + ")"),
            xaxis=dict(
                title='Net-Return'
            ),
            yaxis=dict(
                title='Frequency'
            ),
        )

        plotly.offline.plot({"data": data, "layout":layout})
        time.sleep(1)

        # plotly.offline.plot({"data": data, "layout": layout}, filename=(savename) + ".html")



    def generate_cartesian_product(self, a,b):

        temp = []
        for t1 in a:
            for t2 in b:
                temp += [(t1, t2),]
        return temp



    def get_transformed_index_data(self):

        df = pd.read_csv(self.dir_path + "\\index_csvs\\" + self.index_name + ".csv")
        print("index_name: ", self.index_name)
        df.columns = map(str.lower, df.columns)
        df = df.dropna()
        df["index_close_delta"] = (df["close"]) / (df["close"].shift)(1) - 1
        df = df.dropna()
        return (df)

    def print_stock_dict(self):
        print(self.stock_return_dict)

    def calc_cum_return(self, w, k):

        if self.strategy == 1:

            print( "Initiating Strategy 1: Buy on day (n) at (close) if  Δsp is < (μ – kσ), sell on next day at (open)." )

            cum_sum = 0
            event_count = 0
            index_delta_dict = self.index_df.set_index('date').to_dict()['close']


            for i in self.micro_cap_list:

                stock_df = pd.read_csv(self.dir_path + "\\stock_csvs\\" + i +".csv")
                stock_df.columns = map(str.lower, stock_df.columns)
                stock_df = stock_df.dropna()
                stock_df = stock_df.drop(columns=['low', 'high', 'adj close', 'volume'])
                stock_df['index_close'] = stock_df['date'].map(index_delta_dict)
                stock_df = stock_df.rename(index=str, columns={"close": "stock_close", "open": "stock_open"})
                stock_df["index_close_delta"] = ((stock_df["index_close"] - (stock_df["index_close"].shift)(1)) / (stock_df["index_close"].shift)(1))
                stock_df["stock_close_delta"] = (((stock_df["stock_close"]) - (stock_df["stock_close"].shift)(1)) / (stock_df["stock_close"].shift)(1))
                stock_df["net_close_delta"] = ((stock_df["stock_close_delta"]) - stock_df["index_close_delta"])
                stock_df["ncd_rolling_std"] = stock_df["net_close_delta"].rolling(w).std()  #add shift(1) before rolling to not include that rows day in the calculation
                stock_df["ncd_rolling_mean"] = stock_df["net_close_delta"].rolling(w).mean()
                stock_df["ncd_daily_k_stds"] = stock_df["net_close_delta"] / stock_df["ncd_rolling_std"]
                stock_df['mu_-_k_*_sd'] = ( stock_df["ncd_rolling_mean"] - (k*stock_df["ncd_rolling_std"]))
                stock_df['event_flag'] = np.where(stock_df['net_close_delta'] <( stock_df["ncd_rolling_mean"] - (k*stock_df["ncd_rolling_std"])), 1, 0)

                stock_df["return"] = ((self.investment / stock_df["stock_close"]) * stock_df["stock_open"].shift(-1))*stock_df['event_flag']
                stock_df["net_return"] = (stock_df["return"] - self.investment - self.transaction_cost) * stock_df['event_flag']
                stock_df["roi"] = (stock_df["net_return"] / self.investment)
                cum_sum = cum_sum + (stock_df["net_return"].sum())
                event_count += (stock_df["event_flag"].sum())
                print(i, " : ", (stock_df["net_return"].sum()))
                self.stock_return_dict[i] += cum_sum
                self.stock_transaction_count_dict[i] += event_count


            print("\n")
            print("Stock Name: ", i)
            print("Trailing Window: ", w)
            print("STD Threshold: ", k)
            print("Total portfolio return: ", cum_sum)

            return cum_sum


        if self.strategy == 2:

            print( "Initiating Strategy 2: Buy on day (n) at (close) if   Δsp is < (μ – kσ), sell on next day at (close)." )

            cum_sum = 0
            event_count = 0
            index_delta_dict = self.index_df.set_index('date').to_dict()['close']

            for i in self.micro_cap_list:

                stock_df = pd.read_csv(self.dir_path + "\\stock_csvs\\" + i + ".csv")
                stock_df.columns = map(str.lower, stock_df.columns)
                stock_df = stock_df.dropna()
                stock_df = stock_df.drop(columns=['low', 'high', 'adj close', 'volume'])
                stock_df['index_close'] = stock_df['date'].map(index_delta_dict)
                stock_df = stock_df.rename(index=str, columns={"close": "stock_close", "open": "stock_open"})
                stock_df["index_close_delta"] = ((stock_df["index_close"] - (stock_df["index_close"].shift)(1)) / (stock_df["index_close"].shift)(1))
                stock_df["stock_close_delta"] = (((stock_df["stock_close"]) - (stock_df["stock_close"].shift)(1)) / (stock_df["stock_close"].shift)(1))
                stock_df["net_close_delta"] = ((stock_df["stock_close_delta"]) - stock_df["index_close_delta"])
                stock_df["ncd_rolling_std"] = stock_df["net_close_delta"].rolling(w).std()
                stock_df["ncd_rolling_mean"] = stock_df["net_close_delta"].rolling(w).mean()
                stock_df["ncd_daily_k_stds"] = stock_df["net_close_delta"] / stock_df["ncd_rolling_std"]
                stock_df['mu_-_k_*_sd'] = (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"]))

                stock_df['event_flag'] = np.where(stock_df['net_close_delta'] < (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"])), 1, 0)
                stock_df["return"] = ((self.investment / stock_df["stock_close"]) * stock_df["stock_close"].shift(-1)) *  stock_df['event_flag']
                stock_df["net_return"] = (stock_df["return"] - self.investment - self.transaction_cost) * stock_df['event_flag']
                stock_df["roi"] = (stock_df["net_return"] / self.investment)
                cum_sum = cum_sum + (stock_df["net_return"].sum())
                event_count += (stock_df["event_flag"].sum())
                print(i, " : ", (stock_df["net_return"].sum()))
                self.stock_return_dict[i] += cum_sum
                self.stock_transaction_count_dict[i] += event_count


            print("\n")
            print("Stock Name: ", i)
            print("Trailing Window: ", w)
            print("STD Threshold: ", k)
            print("Total portfolio return: ", cum_sum)

            return cum_sum




        if self.strategy == 3:


            print( "Initiating Strategy 3: Buy on next day’s (n+1) at (close) if  Δsp is < (μ – kσ), sell on following day (n+2) at (open)." )

            cum_sum = 0
            event_count = 0
            index_delta_dict = self.index_df.set_index('date').to_dict()['close']

            for i in self.micro_cap_list:

                stock_df = pd.read_csv(self.dir_path + "\\stock_csvs\\" + i + ".csv")
                stock_df.columns = map(str.lower, stock_df.columns)
                stock_df = stock_df.dropna()
                stock_df = stock_df.drop(columns=['low', 'high', 'adj close', 'volume'])
                stock_df['index_close'] = stock_df['date'].map(index_delta_dict)
                stock_df = stock_df.rename(index=str, columns={"close": "stock_close", "open": "stock_open"})
                stock_df["index_close_delta"] = ((stock_df["index_close"] - (stock_df["index_close"].shift)(1)) / (stock_df["index_close"].shift)(1))
                stock_df["stock_close_delta"] = (((stock_df["stock_close"]) - (stock_df["stock_close"].shift)(1)) / (stock_df["stock_close"].shift)(1))
                stock_df["net_close_delta"] = ((stock_df["stock_close_delta"]) - stock_df["index_close_delta"])
                stock_df["ncd_rolling_std"] = stock_df["net_close_delta"].rolling(w).std()
                stock_df["ncd_rolling_mean"] = stock_df["net_close_delta"].rolling(w).mean()
                stock_df["ncd_daily_k_stds"] = stock_df["net_close_delta"] / stock_df["ncd_rolling_std"]
                stock_df['mu_-_k_*_sd'] = (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"]))

                stock_df['event_flag'] = np.where(stock_df['net_close_delta'] < (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"])), 1, 0)
                stock_df["return"] = (self.investment / (stock_df["stock_close"].shift(-1)) * (stock_df["stock_open"].shift)(-2)) * stock_df['event_flag']
                stock_df["net_return"] = (stock_df["return"] - self.investment - self.transaction_cost) * stock_df['event_flag']
                stock_df["roi"] = (stock_df["net_return"] / self.investment)
                cum_sum = cum_sum + (stock_df["net_return"].sum())
                event_count += (stock_df["event_flag"].sum())
                print(i, " : ", (stock_df["net_return"].sum()))
                self.stock_return_dict[i] += cum_sum
                self.stock_transaction_count_dict[i] += event_count


            print("\n")
            print("Stock Name: ", i)
            print("Trailing Window: ", w)
            print("STD Threshold: ", k)
            print("Total portfolio return: ", cum_sum)

            return cum_sum




        if self.strategy == 4:


            print( "Initiating Strategy 4: Buy on next day’s (n+1) at (close) if  Δsp is < (μ – kσ), sell on following day (n+2) at (close)." )


            cum_sum = 0
            event_count = 0
            index_delta_dict = self.index_df.set_index('date').to_dict()['close']

            for i in self.micro_cap_list:

                stock_df = pd.read_csv(self.dir_path + "\\stock_csvs\\" + i + ".csv")
                stock_df.columns = map(str.lower, stock_df.columns)
                stock_df = stock_df.dropna()
                stock_df = stock_df.drop(columns=['low', 'high', 'adj close', 'volume'])
                stock_df['index_close'] = stock_df['date'].map(index_delta_dict)
                stock_df = stock_df.rename(index=str, columns={"close": "stock_close", "open": "stock_open"})
                stock_df["index_close_delta"] = ((stock_df["index_close"] - (stock_df["index_close"].shift)(1)) / (stock_df["index_close"].shift)(1))
                stock_df["stock_close_delta"] = (((stock_df["stock_close"]) - (stock_df["stock_close"].shift)(1)) / (stock_df["stock_close"].shift)(1))
                stock_df["net_close_delta"] = ((stock_df["stock_close_delta"]) - stock_df["index_close_delta"])
                stock_df["ncd_rolling_std"] = stock_df["net_close_delta"].rolling(w).std()
                stock_df["ncd_rolling_mean"] = stock_df["net_close_delta"].rolling(w).mean()
                stock_df["ncd_daily_k_stds"] = stock_df["net_close_delta"] / stock_df["ncd_rolling_std"]
                stock_df['mu_-_k_*_sd'] = (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"]))

                stock_df['event_flag'] = np.where(stock_df['net_close_delta'] < (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"])), 1, 0)
                stock_df["return"] = ((self.investment / stock_df["stock_close"].shift(-1)) * stock_df["stock_close"].shift(-2)) * stock_df['event_flag']
                stock_df["net_return"] = (stock_df["return"] - self.investment - self.transaction_cost) * stock_df['event_flag']
                stock_df["roi"] = (stock_df["net_return"] / self.investment)
                cum_sum = cum_sum + (stock_df["net_return"].sum())
                event_count += (stock_df["event_flag"].sum())
                print(i, " : ", (stock_df["net_return"].sum()))
                self.stock_return_dict[i] += cum_sum
                self.stock_transaction_count_dict[i] += event_count


            print("\n")
            print("Stock Name: ", i)
            print("Trailing Window: ", w)
            print("STD Threshold: ", k)
            print("Total portfolio return: ", cum_sum)

            return cum_sum


        if self.strategy == 5:

            print( "Initiating Strategy 5: Buy on day (n) if if Δsp is < (μ – kσ) and if if  Δvol is > (μ + hσ), sell on following day at (close)." )

            cum_sum = 0
            event_count = 0
            index_delta_dict = self.index_df.set_index('date').to_dict()['close']

            for i in self.micro_cap_list:

                stock_df = pd.read_csv( self.dir_path + "\\stock_csvs\\" + i + ".csv")
                stock_df.columns = map(str.lower, stock_df.columns)
                stock_df = stock_df.dropna()
                stock_df = stock_df.drop(columns=['low', 'high', 'adj close'])
                stock_df['index_close'] = stock_df['date'].map(index_delta_dict)
                stock_df = stock_df.rename(index=str, columns={"close": "stock_close", "open": "stock_open", "volume": "stock_volume"})
                stock_df["index_close_delta"] = ((stock_df["index_close"] - (stock_df["index_close"].shift)(1)) / (stock_df["index_close"].shift)(1))
                stock_df["stock_close_delta"] = (((stock_df["stock_close"]) - (stock_df["stock_close"].shift)(1)) / (stock_df["stock_close"].shift)(1))
                stock_df["net_close_delta"] = ((stock_df["stock_close_delta"]) - stock_df["index_close_delta"])
                stock_df["volume_delta"] = (((stock_df["stock_volume"]) - (stock_df["stock_volume"].shift)(1)) / (stock_df["stock_volume"].shift)(1))
                stock_df["volume_rolling_std"] = stock_df["volume_delta"].rolling(w).std()
                stock_df["volume_rolling_mean"] = stock_df["volume_delta"].rolling(w).mean()
                stock_df["volume_k_stds"] = stock_df["volume_delta"] / stock_df["volume_rolling_std"]
                stock_df["ncd_rolling_std"] = stock_df["net_close_delta"].rolling(w).std()  # add shift(1) before rolling to not include that rows day in the calculation
                stock_df["ncd_rolling_mean"] = stock_df["net_close_delta"].rolling(w).mean()
                stock_df["ncd_daily_k_stds"] = stock_df["net_close_delta"] / stock_df["ncd_rolling_std"]
                stock_df['mu_-_k_*_sd'] = (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"]))

                stock_df['event_flag'] = np.where((stock_df['net_close_delta'] < (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"]))) & \
                    (stock_df['volume_delta'] > (stock_df["volume_rolling_mean"] + (2 * stock_df["volume_rolling_std"]))), 1, 0)
                stock_df["return"] = (self.investment / (stock_df["stock_close"]) * (stock_df["stock_open"].shift)(-1)) * stock_df['event_flag']
                stock_df["net_return"] = (stock_df["return"] - self.investment - self.transaction_cost) * stock_df['event_flag']
                stock_df["roi"] = (stock_df["net_return"] / self.investment)
                cum_sum = cum_sum + (stock_df["net_return"].sum())
                event_count += (stock_df["event_flag"].sum())
                self.stock_return_dict[i] += cum_sum
                self.stock_transaction_count_dict[i] += event_count

                print(i, " : ", (stock_df["net_return"].sum()))

            print("\n")
            print("Stock Name: ", i)
            print("Trailing Window: ", w)
            print("STD Threshold: ", k)
            print("Total portfolio return: ", cum_sum)
            return cum_sum




        if self.strategy == 6:

            print( "Initiating Strategy 6: Short on day at (close) if  Δsp is < (μ – kσ), return on next day at (open)." )

            cum_sum = 0
            event_count = 0
            index_delta_dict = self.index_df.set_index('date').to_dict()['close']

            for i in self.micro_cap_list:

                stock_df = pd.read_csv(self.dir_path + "\\stock_csvs\\" + i + ".csv")
                stock_df.columns = map(str.lower, stock_df.columns)
                stock_df = stock_df.dropna()
                stock_df = stock_df.drop(columns=['low', 'high', 'adj close'])
                stock_df['index_close'] = stock_df['date'].map(index_delta_dict)
                stock_df = stock_df.rename(index=str, columns={"close": "stock_close", "open": "stock_open", "volume": "stock_volume"})
                stock_df["index_close_delta"] = ((stock_df["index_close"] - (stock_df["index_close"].shift)(1)) / (stock_df["index_close"].shift)(1))
                stock_df["stock_close_delta"] = (((stock_df["stock_close"]) - (stock_df["stock_close"].shift)(1)) / (stock_df["stock_close"].shift)(1))
                stock_df["net_close_delta"] = ((stock_df["stock_close_delta"]) - stock_df["index_close_delta"])
                stock_df["volume_delta"] = (((stock_df["stock_volume"]) - (stock_df["stock_volume"].shift)(1)) / (stock_df["stock_volume"].shift)(1))
                stock_df["volume_rolling_std"] = stock_df["volume_delta"].rolling(w).std()
                stock_df["volume_rolling_mean"] = stock_df["volume_delta"].rolling(w).mean()
                stock_df["volume_k_stds"] = stock_df["volume_delta"] / stock_df["volume_rolling_std"]
                stock_df["ncd_rolling_std"] = stock_df["net_close_delta"].rolling(w).std()
                stock_df["ncd_rolling_mean"] = stock_df["net_close_delta"].rolling(w).mean()
                stock_df["ncd_daily_k_stds"] = stock_df["net_close_delta"] / stock_df["ncd_rolling_std"]
                stock_df['mu_-_k_*_sd'] = (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"]))

                stock_df['event_flag'] = np.where((stock_df['net_close_delta'] < (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"]))), 1, 0)
                stock_df["return"] = (self.investment + (self.investment - (self.investment / stock_df["stock_close"] * stock_df["stock_open"].shift(-1)))) * stock_df['event_flag']
                stock_df["net_return"] = (stock_df["return"] - self.investment -  self.transaction_cost) * stock_df['event_flag']
                stock_df["roi"] = (stock_df["net_return"] / self.investment)
                cum_sum = cum_sum + (stock_df["net_return"].sum())
                event_count += (stock_df["event_flag"].sum())
                print(i, " : ", (stock_df["net_return"].sum()))
                self.stock_return_dict[i] += cum_sum
                self.stock_transaction_count_dict[i] += event_count


            print("\n")
            print("Stock Name: ", i)
            print("Trailing Window: ", w)
            print("STD Threshold: ", k)
            print("Total portfolio return: ", cum_sum)

            return cum_sum




        if self.strategy == 7:

                print("Initializing Strategy 7: Buy on day (n) at (typical price) if  Δsp is < (μ – kσ), sell on next day at (open).")

                cum_sum = 0
                event_count = 0
                index_delta_dict = self.index_df.set_index('date').to_dict()['close']

                for i in self.micro_cap_list:

                    stock_df = pd.read_csv(self.dir_path + "\\stock_csvs\\" + i + ".csv")
                    stock_df.columns = map(str.lower, stock_df.columns)
                    stock_df = stock_df.dropna()
                    stock_df = stock_df.drop(columns=['adj close', 'volume'])
                    stock_df['index_close'] = stock_df['date'].map(index_delta_dict)
                    stock_df = stock_df.rename(index=str, columns={"close": "stock_close", "open": "stock_open", "low": "stock_low", "high": "stock_high"})
                    stock_df["index_close_delta"] = ((stock_df["index_close"] - (stock_df["index_close"].shift)(1)) / (stock_df["index_close"].shift)(1))
                    stock_df["stock_close_delta"] = (((stock_df["stock_close"]) - (stock_df["stock_close"].shift)(1)) / (stock_df["stock_close"].shift)(1))
                    stock_df["net_close_delta"] = ((stock_df["stock_close_delta"]) - stock_df["index_close_delta"])
                    stock_df["ncd_rolling_std"] = stock_df["net_close_delta"].rolling(w).std()
                    stock_df["ncd_rolling_mean"] = stock_df["net_close_delta"].rolling(w).mean()
                    stock_df["ncd_daily_k_stds"] = stock_df["net_close_delta"] / stock_df["ncd_rolling_std"]
                    stock_df['mu_-_k_*_sd'] = (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"]))
                    stock_df["typical"] = ((stock_df["stock_high"] + stock_df["stock_low"] + stock_df["stock_open"] + stock_df["stock_close"]) / 4)

                    stock_df['event_flag'] = np.where(stock_df['net_close_delta'] < (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"])), 1, 0)
                    stock_df["return"] = ((self.investment / stock_df["typical"]) * stock_df["stock_open"].shift(-1)) * stock_df['event_flag']
                    stock_df["net_return"] = (stock_df["return"] - self.investment -  self.transaction_cost) * stock_df['event_flag']
                    stock_df["roi"] = (stock_df["net_return"] / self.investment)
                    cum_sum = cum_sum + (stock_df["net_return"].sum())
                    event_count += (stock_df["event_flag"].sum())
                    print(i, " : ", (stock_df["net_return"].sum()))
                    self.stock_return_dict[i] += cum_sum
                    self.stock_transaction_count_dict[i] += event_count

                print("\n")
                print("Stock Name: ", i)
                print("Trailing Window: ", w)
                print("STD Threshold: ", k)
                print("Total portfolio return: ", cum_sum)

                return cum_sum



        if self.strategy == 8:

                print("Initializing Strategy 8: Buy on day (n) at (typical price) if  Δsp is < (μ – kσ), sell on next day at (close).")

                cum_sum = 0
                event_count = 0
                index_delta_dict = self.index_df.set_index('date').to_dict()['close']

                for i in self.micro_cap_list:

                    stock_df = pd.read_csv(self.dir_path + "\\stock_csvs\\" + i + ".csv")
                    stock_df.columns = map(str.lower, stock_df.columns)
                    stock_df = stock_df.dropna()
                    stock_df = stock_df.drop(columns=['adj close', 'volume'])
                    stock_df['index_close'] = stock_df['date'].map(index_delta_dict)
                    stock_df = stock_df.rename(index=str, columns={"close": "stock_close", "open": "stock_open", "low": "stock_low", "high": "stock_high"})
                    stock_df["index_close_delta"] = ((stock_df["index_close"] - (stock_df["index_close"].shift)(1)) / (stock_df["index_close"].shift)(1))
                    stock_df["stock_close_delta"] = (((stock_df["stock_close"]) - (stock_df["stock_close"].shift)(1)) / (stock_df["stock_close"].shift)(1))
                    stock_df["net_close_delta"] = ((stock_df["stock_close_delta"]) - stock_df["index_close_delta"])
                    stock_df["ncd_rolling_std"] = stock_df["net_close_delta"].rolling(w).std()
                    stock_df["ncd_rolling_mean"] = stock_df["net_close_delta"].rolling(w).mean()
                    stock_df["ncd_daily_k_stds"] = stock_df["net_close_delta"] / stock_df["ncd_rolling_std"]
                    stock_df['mu_-_k_*_sd'] = (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"]))
                    stock_df["typical"] = ((stock_df["stock_high"] + stock_df["stock_low"] + stock_df["stock_open"] + stock_df["stock_close"]) / 4)

                    stock_df['event_flag'] = np.where(stock_df['net_close_delta'] < (stock_df["ncd_rolling_mean"] - (k * stock_df["ncd_rolling_std"])), 1, 0)
                    stock_df["return"] = ((self.investment / stock_df["typical"]) * stock_df["stock_close"].shift(-1)) * stock_df['event_flag']
                    stock_df["net_return"] = (stock_df["return"] - self.investment - self.transaction_cost) * stock_df['event_flag']
                    stock_df["roi"] = (stock_df["net_return"] / self.investment)

                    cum_sum = cum_sum + (stock_df["net_return"].sum())
                    event_count += (stock_df["event_flag"].sum())

                    print(i, " : ", (stock_df["net_return"].sum()))
                    self.stock_return_dict[i] += cum_sum
                    self.stock_transaction_count_dict[i] += event_count

                print("\n")
                print("Stock Name: ", i)
                print("Trailing Window: ", w)
                print("STD Threshold: ", k)
                print("Total portfolio return: ", cum_sum)

                return cum_sum





# Implementation (Set i to the max number of strategies)
##########################################################


for i in range(8):
    model_1 = backtest(strategy=i, index_name="XBI")
    model_1.plot_net_return_scatterplot()
    model_1.plot_net_return_histogram(15)
    model_1.plot_top_average_stock_returns(15)

