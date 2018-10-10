import numpy as np
import pandas as pd
import os
import time
import plotly
import plotly.offline
import plotly.graph_objs as go
import os


"Strategy 2:  Buy on day (n) at close if Δsp is < (μ – kσ), sell on next day at closing price"



dir_path = os.path.dirname(os.path.realpath(__file__))

# TODO: Add script to isolate and visualize recognized events.  (i.e. save the +- 20 rows around a detected event and visualize)

#
# TODO: Add two new features to each Pandas dataframe :
# i.	ROI column (return/ risked investment)
# ii.	Roi_flag column (indicating when an event has taken place)

# TODO: Round decimal on plotly overlay

global transaction_cost
transaction_cost = 0.00

global benchmark_index
benchmark_index = "XBI"

global strategy
strategy = "Strategy 2"



def main():
    print( "Simulating trading strategy on " + str(len(micro_cap_list)) + " id cap biotech companies")
    start_time = time.time()


    #big trial (20 - 30 min runtime)
    std_trailing_window_inputs = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)   # trailing_sd window
    std_threshold = (.25, .5, .75, 1, 1.25, 1.5, 1.75, 2, 2.25,  2.5, 2.75,  3, 3.25,  3.5)  # standard_dev sampling window



    #small trial
    # std_trailing_window_inputs = (6, 8, 10, 12)   # trailing_sd window
    # std_threshold = (0.5, 1, 1.5, 2, 2.5, 3)  # standard_dev sampling window
    investment = 100  # investment level per arbitrage event

    return_list = generate_net_return_list(std_trailing_window_inputs, std_threshold, investment, benchmark_index)
    create_scatterplot(return_list)


    print(return_list)
    print("\n--- %s seconds ---" % (time.time() - start_time))
    print("\n--- %s minutes ---" % (((time.time() - start_time))/60))




def create_scatterplot(return_list):

    std_trailing_window = return_list[0]
    std_threshold = return_list[1]
    net_returns = return_list[2]

    scaled_net_returns = []  # scale down return
    for x in net_returns:
        y = x/ max(net_returns)
        scaled_net_returns.append(abs(y) * 30)

    max_val = max( max(net_returns), abs(min(net_returns)))

    print(std_trailing_window)
    print(std_threshold)
    print(net_returns)

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

    layout = go.Layout(title= str("Net-Return Spread ( " + strategy + ", Index = " + benchmark_index + ", Transaction Cost = $" + str(transaction_cost) + ")"),
                       xaxis=dict(title='Rolling σ Window Length'),
                       yaxis=dict(title='σ Threshold'),
                       hovermode='closest'
                       )
    plotly.offline.plot({"data": data, "layout": layout})




def generate_net_return_list( w_tup, k_tup, investment, index_name):

    combo_list = (generate_cartesian_product(w_tup, k_tup))
    print(combo_list)
    counter = 0

    w_list = []
    k_list = []
    net_return_list = []

    # index_df creation line should be here, so it doesnt need to be created for each investment simulation
    index_df = get_transformed_index_data(index_name = benchmark_index)

    print(index_df.tail(10))

    for i in combo_list:

        counter += 1
        w = i[0]
        k = i[1]
        net_return = calc_return(w, k, investment, index_df)

        w_list.append(w)
        k_list.append(k)
        net_return_list.append(net_return)

        print(net_return)
        print("****************************************", len(combo_list) - counter, "Calculations Remaining ****************************************\n")

    return[tuple(w_list), tuple(k_list), tuple(net_return_list)]




def calc_return(w, k, investment, index_df):

    cum_sum = 0
    event_count = 0
    max_sum = 0  #for debugging printout
    index_delta_dict = index_df.set_index('date').to_dict()['close']


    for i in micro_cap_list:

        stock_df = pd.read_csv(dir_path + "\\stock_csvs\\" + i +".csv")  #TODO: Make dynamic (so it forms a list from the subdirectory names alone)
        stock_df.columns = map(str.lower, stock_df.columns)
        stock_df = stock_df.dropna()
        stock_df = stock_df.drop(columns=['low', 'high', 'adj close', 'volume'])


        # map index dictionary (date: delta) to a new column on each stock's dataframe
        stock_df['index_close'] = stock_df['date'].map(index_delta_dict)
        stock_df = stock_df.rename(index=str, columns={"close": "stock_close", "open": "stock_open"})


        stock_df["index_close_delta"] = ((stock_df["index_close"] - (stock_df["index_close"].shift)(1)) / (stock_df["index_close"].shift)(1))
        stock_df["stock_close_delta"] = (((stock_df["stock_close"]) - (stock_df["stock_close"].shift)(1)) / (stock_df["stock_close"].shift)(1))

        # Remove Tracking Error
        stock_df["net_close_delta"] = ((stock_df["stock_close_delta"]) - stock_df["index_close_delta"])

        #ndc = net close delta
        stock_df["ncd_rolling_std"] = stock_df["net_close_delta"].rolling(w).std()  #add shift(1) before rolling to not include that rows day in the calculation
        stock_df["ncd_rolling_mean"] = stock_df["net_close_delta"].rolling(w).mean()
        stock_df["ncd_daily_k_stds"] = stock_df["net_close_delta"] / stock_df["ncd_rolling_std"]
        stock_df['mu_-_k_*_sd'] = ( stock_df["ncd_rolling_mean"] - (k*stock_df["ncd_rolling_std"]))
        stock_df['event_flag'] = np.where(stock_df['net_close_delta'] <( stock_df["ncd_rolling_mean"] - (k*stock_df["ncd_rolling_std"])), 1, 0)

        # stock_df['event_flag'] = np.where(stock_df['ncd_daily_k_stds'] <= -k, 1, 0)

        #TODO: SAVE THE (DATE: PRICE) VALUES FOR EXTREME EVENTS


        stock_df["return"] = (investment / (stock_df["stock_close"]) * (stock_df["stock_close"].shift)(-1))*stock_df['event_flag']
        stock_df["net_return"] = (stock_df["return"] - investment - transaction_cost) * stock_df['event_flag']
        stock_df["roi"] = (stock_df["net_return"] / investment)


        # print("Stock Name: ", i)
        # print("Trailing Window: ", w)
        # print("STD Threshold: ", k)
        # print(stock_df.tail(10))

        cum_sum = cum_sum + (stock_df["net_return"].sum())
        event_count += (stock_df["event_flag"].sum())



        if i == "ABEO":
            df.to_csv(i + "_strategy_2.csv")

        print(i, " : ", (stock_df["net_return"].sum()))
        # print(df)


    print("\n")

    print("Stock Name: ", i)
    print("Trailing Window: ", w)
    print("STD Threshold: ", k)
    # print("Max Sum: ", max_sum)
    # print("Event_Count: ", event_count)
    # print("Total Vested (Pre-Return): ", event_count  * p )
    print("Total portfolio return: ", cum_sum)
    # print("Average portfolio return: ", cum_sum/event_count)

    return cum_sum




def get_transformed_index_data(index_name):

    df = pd.read_csv(dir_path + "\\index_csvs\\" + index_name + ".csv")
    print("index_name: ", index_name)
    df.columns = map(str.lower, df.columns)
    df = df.dropna()
    df["index_close_delta"] = (df["close"]) / (df["close"].shift)(1) - 1
    df = df.dropna()
    return(df)




def generate_cartesian_product(a,b):

    temp = []

    for t1 in a:
        for t2 in b:
            temp += [(t1, t2),]

    return temp



global  micro_cap_list
micro_cap_list = [ "ALDX", "BLRX", "KDMN", "KALV", "KMDA", "MDGL", "PTGX", "RETA", "TRVN", "CDTX", \
                       "MTNB", "NBRV", "KIN", "XOMA", "CMRX", "CTRV", "NNVC", "CDXS", "PFNX", "ATNM", "AGLE", "AFMD", \
                       "ALRN", "AVEO", "BTAI",  "ECYT", "FBIO", "GALT", \
                       "GNPX", "GTXI", "IMDZ", "IMGN", "IMMP", "INFI", "KURA", "LPTX", "MEIP", "MRTX", "NK", "ONS", \
                       "PIRS", "RNN", "SLS", "SRNE", "STML", "SNSS", "TRIL", "VBLT", "VSTM",  \
                       "ZYME", "ZYNE", "AXSM", "NTEC", "NERV", \
                       "TENX", "KRYS", "MNKD", "NEPT", "ADVM", "AGTC", "IMMY",  "OCUL", "OHRP", "OPHT", \
                       "OVAS", "RDHL", "PLX", "GNMX", "GEMP", "SELB", "CALA", "ADMA", "ASNS", "CFRX", "DVAX", \
                       "SGMO", "SMMT", "MTFB", "SPRO", "AMPE", "ABUS", "ARWR", "CNAT", "DRNA", "GLMD", "VTL", "ALNA", \
                       "CBAY",   "EDGE", "MNOV", "OVID", "FLKS", "DRRX", "ABEO", "AKTX", "LIFE", "CATB", \
                       "CPRX", "CHMA", "EIGR", "FATE", "NVLN", "RGLS", "RCKT", "SBBP", "QURE", "XENE", "ATHX", "PRQR",\
                       "PULM", "VRNA", "ARCT", "GLYC", "NYMX", "SPHS", "URGN", "GNCA",  "SBPH", "VVUS", \
                       "ZFGN", "OBSV"]



if __name__ == "__main__":
    main()
