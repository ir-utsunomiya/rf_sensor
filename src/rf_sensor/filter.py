import pandas as pd
import numpy as np

def filter_min_distance(df_list,**kwargs):
    verbose = kwargs.get('verbose',False)
    min_update_d = kwargs.get('min_update_d',1.0)

    df_last = df_list[0]
    x_last  = df_last.iloc[0]['x']
    y_last  = df_last.iloc[0]['y']
    df_list_update   = list()
    min_update_dist2 = min_update_d**2

    for df_ in df_list[1:]:
        x_ = df_.iloc[0]['x']
        y_ = df_.iloc[0]['y']
        distance_ = (x_-x_last)**2+(y_-y_last)**2
        if distance_ > min_update_dist2: #if more than min_distance, add data point
            df_list_update.append(df_last)
            df_last = df_
            if verbose: print('{:5.2f}: Add  - Xlast: [{:5.2f},{:5.2f}] Xnew: [{:5.2f},{:5.2f}]'.format(
                                                                                distance_**.5,x_last,y_last,x_,y_))
            x_last = x_
            y_last = y_
        else: #if not, add current measure to previous point and continue
            df_last = df_last.append(df_)
            if verbose: print('{:5.2f}: Comb - Xlast: [{:5.2f},{:5.2f}] Xnew: [{:5.2f},{:5.2f}]'.format(
                                                                                distance_**.5,x_last,y_last,x_,y_))

    #add last point regardless
    df_list_update.append(df_last)
    df_list = df_list_update
    return df_list_update
