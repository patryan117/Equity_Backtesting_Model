import numpy as np
import pandas as pd
import os
import time
import plotly
import plotly.offline
import plotly.graph_objs as go



dir_path = os.path.dirname(os.path.realpath(__file__))

#TODO set so that the creating loop doesnt take from the hard coded list, but parses from the /data/ folder
#TODO add segment to collect data that creates an interger feature for stock splits (holding the split ratio), and does one of two options:
    # manipulates the investment in accordance with the split
    # does not allow the algorithm to trade the date before or after the stock split







def main():

    start_time = time.time()

    std_trailing_window_inputs = (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)   # trailing_sd window
    std_threshold = (.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)  # standard_dev sampling window
    investment = 100

    return_list = generate_net_return_list(std_trailing_window_inputs, std_threshold, investment)
    create_heated_scatterplot(return_list)

    print(return_list)
    print("\n--- %s seconds ---" % (time.time() - start_time))
    print("\n--- %s minutes ---" % (((time.time() - start_time))/60))




def create_heated_scatterplot(return_list):

    std_trailing_window = return_list[0]
    std_threshold = return_list[1]
    net_returns = return_list[2]

    trace1 = go.Scatter(
        y = std_threshold,
        x = std_trailing_window,
        mode='markers',
        text=net_returns,
        marker=dict(
            size=16,
            color = net_returns, #set color equal to a variable
            colorscale='Viridis',
            showscale=True
        )
    )

    data = [trace1]


    plotly.offline.plot({"data": data,
                         "layout": go.Layout(title="hello world",

                          )},
                         image_filename='test')








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

        print("\n**************************************", len(combo_list) - counter, "Calculations Remaining ****************************************")
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
        df["daily_k_stds"] = df["close_delta"] / df["rolling_std"]
        df['event_flag'] = np.where(df['daily_k_stds'] <= -k, 1, 0)
        df["return"] = (p / (df["close"]) * (df["close"].shift)(-1))*df['event_flag']
        df["net_return"] = (df["return"] - p) * df['event_flag']

        cum_sum = cum_sum + (df["net_return"].sum())
        event_count += (df["event_flag"].sum())

        if (df["net_return"].sum()) > max_sum:
            max_sum = (df["net_return"].sum())


        if i == "MDWD":
            df.to_csv("trouble.csv")

        # print(i, " : ", (df["net_return"].sum()))
        # print(df)

    # print("\n")
    # print("Max Sum: ", max_sum)
    # print("Event_Count: ", event_count)
    # print("Total Vested (Pre-Return): ", event_count  * p )
    # print("Total portfolio return: ", cum_sum)
    # print("Average portfolio return: ", cum_sum/event_count)

    return cum_sum




def generate_cartesian_product(a,b):


    temp = []

    for t1 in a:
        for t2 in b:
            temp += [(t1, t2),]

    return temp


global  micro_cap_list
micro_cap_list = [ "ALDX", "BLRX", "CRMD", "KDMN", "KALV", "KMDA", "MDGL", "MGEN", "PTGX", "RETA", "TRVN", "CDTX", \
                   "MTNB", "NBRV", "KIN", "XOMA", "CMRX", "CTRV", "NNVC", "CDXS", "PFNX", "ATNM", "AGLE", "AFMD", \
                   "ALRN", "AVEO", "BPTH", "BTAI",  "CBMG", "DFFN", "ECYT", "FBIO", "GALT", \
                   "GNPX", "GTXI", "IMDZ", "IMGN", "IMMP", "INFI", "KURA", "LPTX", "MEIP", "MRTX", "NK", "ONS", \
                   "PIRS", "RNN", "SLS", "SRNE", "STML", "SNSS",  "TCON", "TRIL", "VBLT", "VSTM",  \
                   "ZYME", "ZYNE", "AVXL", "AXSM", "NTEC", \
                   "OVAS", "RDHL", "PLX", "GNMX", "CAPR", "GEMP", "SELB", "CALA", "ADMA", "ASNS", "CFRX", "DVAX", \
                   "SGMO", "SMMT", "MTFB", "SPRO", "AMPE", "ABUS", "ARWR", "CNAT", "DRNA", "GLMD", "VTL", "ALNA", \
                   "CBAY", "SYN", "BCLI", "EDGE", "MNOV", "OVID", "FLKS", "DRRX", "ABEO", "AKTX", "LIFE", "CATB", \
                   "CPRX", "CHMA", "EIGR", "FATE", "NVLN", "RGLS", "RCKT", "SBBP", "QURE", "XENE", "ATHX", "PRQR",\
                   "PULM", "VRNA", "ARCT", "GLYC", "NYMX", "SPHS", "URGN", "GNCA", "SBPH", "VVUS", \
                   "ZFGN", "OBSV", "PTN"]



if __name__ == "__main__":
    main()
