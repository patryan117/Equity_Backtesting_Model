import numpy as np
import pandas as pd
import os

dir_path = os.path.dirname(os.path.realpath(__file__))



def main():

    investment_amt = 100
    cart_tup = (cartesian_product_loop())
    create_close_delta_feature()

def create_close_delta_feature():
    for x in micro_cap_list:
        df = pd.read_csv(dir_path + "\\data\\" + x +".csv")
        # df[7] = float(df[5]) / float(df[5].shift)(1) - 1
        print(df[7])






def cartesian_product_loop():
    w_tup = (5,6,7,8,9,10,11,12,13,14,15, 16)  # standard_dev sampling window
    k_typ = (.5, 1, 1.5, 2, 2.5, 3, 3.5)  #

    res = ()

    for t1 in w_tup:
        for t2 in k_typ:
            res += ((t1, t2),)

    return res


global  micro_cap_list
micro_cap_list = [ "ALDX", "BLRX", "CRMD", "KDMN", "KALV", "KMDA", "MDGL", "MGEN", "PTGX", "RETA", "TRVN", "CDTX", \
                   "MTNB", "NBRV", "KIN", "XOMA", "CMRX", "CTRV", "NNVC", "CDXS", "PFNX", "ATNM", "AGLE", "AFMD", \
                   "ALRN", "AVEO", "BPTH", "BTAI", "CASI", "CBMG", "CGEN", "CTIC", "DFFN", "ECYT", "FBIO", "GALT", \
                   "GNPX", "GTXI", "IMDZ", "IMGN", "IMMP", "INFI", "KURA", "LPTX", "MEIP", "MRTX", "NK", "ONS", \
                   "PIRS", "RNN", "SLS", "SRNE", "STML", "SNSS", "SNDX", "TOCA", "TCON", "TRIL", "VBLT", "VSTM",  \
                   "ZYME", "ZYNE", "AST", "CYAD", "CUR", "PSTI", "VCEL", "AVXL", "AXSM", "NTEC", "NERV", "TTNP", \
                   "TENX", "KRYS", "MNKD", "NEPT", "ADVM", "AGTC", "CLSD", "IMMY", "NBY", "OCUL", "OHRP", "OPHT", \
                   "OVAS", "RDHL", "PLX", "GNMX", "CAPR", "GEMP", "SELB", "CALA", "ADMA", "ASNS", "CFRX", "DVAX", \
                   "SGMO", "SMMT", "MTFB", "SPRO", "AMPE", "ABUS", "ARWR", "CNAT", "DRNA", "GLMD", "VTL", "ALNA", \
                   "CBAY", "SYN", "BCLI", "EDGE", "MNOV", "OVID", "FLKS", "DRRX", "ABEO", "AKTX", "LIFE", "CATB", \
                   "CPRX", "CHMA", "EIGR", "FATE", "NVLN", "RGLS", "RCKT", "SBBP", "QURE", "XENE", "ATHX", "PRQR",\
                   "PTI", "PULM", "VRNA", "ARCT", "GLYC", "NYMX", "SPHS", "URGN", "GNCA", "VBIV", "SBPH", "VVUS", \
                   "ZFGN", "OBSV", "PTN", "MDWD"]



if __name__ == "__main__":
    main()
