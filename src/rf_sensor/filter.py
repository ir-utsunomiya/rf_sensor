import pandas as pd
import numpy as np

def group_time(df,**kwargs):
    verbose    = kwargs.get('verbose',False)
    delta_time = kwargs.get('delta_time',1.) # in seconds
    # computing start and end times
    start_time = np.min(df['secs'])
    end_time   = np.max(df['secs'])
    rss_time_  = np.arange(0,int(1e9)*(end_time-start_time),int(1e9)*delta_time)
    # group dataframe items by time range and generating a list of dataframes per time range
    bins = pd.cut(int(1e9)*(df['secs']-start_time)+df['nsecs'],rss_time_)
    df_group = df.groupby(bins)
    df_list = [group for name, group in df_group]
    if verbose: print('{:25s}: {:}'.format('Number of dataframes',len(df_list)))
    return df_list

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
