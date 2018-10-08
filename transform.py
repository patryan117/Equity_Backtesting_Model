import numpy as np
import pandas as pd
import os
import time
import plotly
import plotly.offline
import plotly.graph_objs as go
import os



dir_path = os.path.dirname(os.path.realpath(__file__))

#TODO set so that the creating loop doesnt take from the hard coded list, but populates from the /stock_csvs/ folder

# TODO add index (weighted by price / volitility)

# TODO: COnfirm that plotly scatterplot is displaying negtaive values in blue colorscale.  (centred on single trace, or split w/ 1 red 1 blue traces)

# TODO Add 4 different trading strategies (probs as different transform.py files)

# TODO: DAdd a separate script in transform.py that calculates and visualizes an index based on the close date of each stock.

# TODO: Add script to isolate and visualize recognized events.  (i.e. save the +- 20 rows around a detected event and visualize)

#
# TODO: Add two new features to each Pandas dataframe :
# i.	ROI column (return/ risked investment)
# ii.	Roi_flag column (indicating when an event has taken place)




def main():
    print( "Simulating trading strategy on " + str(len(micro_cap_list)) + " mid cap companies")
    start_time = time.time()

    # std_trailing_window_inputs = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)   # trailing_sd window
    # std_threshold = (.25, .5, .75, 1, 1.25, 1.5, 1.75, 2, 2.25,  2.5, 2.75,  3, 3.25,  3.5)  # standard_dev sampling window


    std_trailing_window_inputs = (5, 6)   # trailing_sd window
    std_threshold = (2, 2.5)  # standard_dev sampling window
    investment = 100  # investment level per arbitrage event



    return_list = generate_net_return_list(std_trailing_window_inputs, std_threshold, investment, "IBB")
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




def generate_net_return_list( w_tup, k_tup, investment, index_name):

    combo_list = (generate_cartesian_product(w_tup, k_tup))
    counter = 0

    w_list = []
    k_list = []
    net_return_list = []

    # index_df creation line should be here, so it doesnt need to be created for each investment trial
    index_df = get_transformed_index_data(index_name = "IBB")



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

        # print(w_list) ;print(k_list);  print(net_return_list)


    return[tuple(w_list), tuple(k_list), tuple(net_return_list)]




def calc_return(w, k, p, index_df):

    cum_sum = 0
    event_count = 0
    max_sum = 0


    for i in micro_cap_list:

        print(index_df)
        stock_df = pd.read_csv(dir_path + "\\stock_csvs\\" + i +".csv")  #TODO: Make dynamic (so it forms a list from the subdirectory names alone)
        stock_df.columns = map(str.lower, stock_df.columns)
        stock_df = stock_df.dropna()


        # stock_df["index_close_delta"] = stock_df.apply(add_index_close_delta(index_df))


        # cake = add_index_close_delta(stock_df, index_df)
        # print(cake)

        stock_df["index_close_delta"] = np.where(stock_df["date"] == index_df["date"], index_df["index_close_delta"], None)

        df.loc[df['column_name'] == some_value]

        stock_df["stock_close_delta"] = (stock_df["close"]) / (stock_df["close"].shift)(1) - 1

        stock_df["rolling_std"] = stock_df["stock_close_delta"].rolling(w).std()
        stock_df["rolling_mean"] = stock_df["stock_close_delta"].rolling(w).std()
        stock_df["daily_k_stds"] = stock_df["stock_close_delta"] / stock_df["rolling_std"]
        stock_df['event_flag'] = np.where(stock_df['stock_close_delta'] <= stock_df["rolling_mean"] - k*stock_df["rolling_std"], 1, 0)
        stock_df["return"] = (p / (stock_df["close"]) * (stock_df["close"].shift)(-1))*stock_df['event_flag']
        stock_df["net_return"] = (stock_df["return"] - p) * stock_df['event_flag']

        print(i)
        print(stock_df)

        cum_sum = cum_sum + (stock_df["net_return"].sum())
        event_count += (stock_df["event_flag"].sum())

        # if (df["net_return"].sum()) > max_sum:
        #     max_sum = (df["net_return"].sum())


        # if i == "ABEO":
        #     df.to_csv(i + "trouble.csv")

        # print(i, " : ", (df["net_return"].sum()))
        # print(df)


    # print("\n")
    # print("Max Sum: ", max_sum)
    # print("Event_Count: ", event_count)
    # print("Total Vested (Pre-Return): ", event_count  * p )
    print("Total portfolio return: ", cum_sum)
    # print("Average portfolio return: ", cum_sum/event_count)

    return cum_sum


def add_index_close_delta(x):
    out_df = x.apply(lambda y : y["index_close_delta"] if x["date"] == y["date"] else None)
    return out_df



def get_transformed_index_data(index_name = "IBB"):

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


global biotech_index
biotech_index = "XBI"

if __name__ == "__main__":
    main()
