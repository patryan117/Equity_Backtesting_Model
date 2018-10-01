import numpy as np
import pandas as pd
import os
import time
import plotly
import plotly.offline
import plotly.graph_objs as go

dir_path = os.path.dirname(os.path.realpath(__file__))

#TODO set so that the creating loop doesnt take from the hard coded list, but populates from the /data/ folder

#TODO add segment to collect data that creates an interger feature for stock splits (holding the split ratio), and does one of two options:
    # manipulates the investment in accordance with the split (probably best feature)
    # does not allow the algorithm to trade the date before or after the stock split

# TODO add index (weighted by price / volitility)

# TODO Create tracking error correction based on weighted index

# TODO: COnfirm that plotly scatterplot is displaying negtaive values in blue colorscale.  (centred on single trace, or split w/ 1 red 1 blue traces)

# TODO Add 4 different trading strategies (probs as different transform.py files)


# •	Center color scale on scatterplot and add time_window to title (pass start_date and end_date as a string)
#
# •	Add a separate script in transform.py that calculates and visualizes an index based on the close date of each stock.
#
# •	Add script to take produce lineplots of events.  (i.e. save the +- 20 rows around a detected event and visualize)
#
# •	Add one of two options to prevent empty .csv errors:
# i.	Add try-except structure to main feature engineering block (so empty datasets, caused by a early start_date error, are not processed.
# ii.	Or have .csv list populate from the folder, and not follow inputs, and only have the dataset include non-errored sets)
#
# •	Add two new features to each Pandas dataframe :
# i.	ROI column (return/ risked investment)
# ii.	Roi_flag column (indicating when an event has taken place)






def main():

    print( "Simulating trading strategy on " + str(len(micro_cap_list)) + " mid cap companies")
    start_time = time.time()

    std_trailing_window_inputs = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)   # trailing_sd window
    std_threshold = (.25, .5, .75, 1, 1.25, 1.5, 1.75, 2, 2.25,  2.5, 2.75,  3, 3.25,  3.5)  # standard_dev sampling window
    investment = 100  # investment level per arbitrage event

    return_list = generate_net_return_list(std_trailing_window_inputs, std_threshold, investment)
    create_heated_scatterplot(return_list)

    print(return_list)
    print("\n--- %s seconds ---" % (time.time() - start_time))
    print("\n--- %s minutes ---" % (((time.time() - start_time))/60))




def create_heated_scatterplot(return_list):

    std_trailing_window = return_list[0]
    std_threshold = return_list[1]
    net_returns = return_list[2]

    scaled_net_returns = []  # scale down return
    for x in net_returns:
        scaled_net_returns.append(abs(x)/ 200)

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
            showscale=True

    )
    )

    data = [trace0]

    layout = go.Layout(title="Net-Return Spread",
                       xaxis=dict(title='Rolling σ Window Length'),
                       yaxis=dict(title='σ Threshold'),
                       hovermode='closest'
                       )
    plotly.offline.plot({"data": data, "layout": layout})




def generate_net_return_list( w_tup, k_tup, investment):

    combo_list = (generate_cartesian_product(w_tup, k_tup))
    item_list = []
    counter = 0

    w_list = []; k_list = [];   net_return_list = []

    for i in combo_list:
        counter += 1
        w = i[0]
        k = i[1]
        net_return = calc_return(w, k, investment)

        w_list.append(w); k_list.append(k); net_return_list.append(net_return)

        print(net_return)
        print("****************************************", len(combo_list) - counter, "Calculations Remaining ****************************************\n")

        # print(w_list)
        # print(k_list)
        # print(net_return_list)


    return[tuple(w_list), tuple(k_list), tuple(net_return_list)]






def calc_return(w, k, p):

    cum_sum = 0
    event_count = 0
    max_sum = 0

    for i in micro_cap_list:

        df = pd.read_csv(dir_path + "\\data\\" + i +".csv")
        df.columns = map(str.lower, df.columns)
        df = df.dropna()

        df["close_delta"] = (df["close"]) / (df["close"].shift)(1) - 1
        df["rolling_std"] = df["close_delta"].rolling(w).std()
        df["rolling_mean"] = df["close_delta"].rolling(w).std()
        df["daily_k_stds"] = df["close_delta"] / df["rolling_std"]
        df['event_flag'] = np.where(df['close_delta'] <= df["rolling_mean"] - k*df["rolling_std"], 1, 0)
        df["return"] = (p / (df["close"]) * (df["close"].shift)(-1))*df['event_flag']
        df["net_return"] = (df["return"] - p) * df['event_flag']
        # df["net_return"] = (df["return"] - p) * df['event_flag']


        cum_sum = cum_sum + (df["net_return"].sum())
        event_count += (df["event_flag"].sum())

        # if (df["net_return"].sum()) > max_sum:
        #     max_sum = (df["net_return"].sum())


        if i == "ABEO":
            df.to_csv(i + "trouble.csv")

        print(i, " : ", (df["net_return"].sum()))
        # print(df)


    # print("\n")
    # print("Max Sum: ", max_sum)
    # print("Event_Count: ", event_count)
    # print("Total Vested (Pre-Return): ", event_count  * p )
    print("Total portfolio return: ", cum_sum)
    # print("Average portfolio return: ", cum_sum/event_count)

    return cum_sum




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
