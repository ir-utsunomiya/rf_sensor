# Copyright (c) 2019, the rf_sensor authors (see AUTHORS.txt)
# Licensed under the BSD 3-clause license (see LICENSE.txt)

import pandas as pd
import numpy as np

"""
Filters for rss data
"""

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

def stats_mac(df_list,**kwargs):
    verbose = kwargs.get('verbose',False)
    min_readings = kwargs.get('min_readings',3)
    #group by mac and get stats
    df_list_stats = [datum.groupby('mac_address').agg({'data':['mean','std','count'],
                            'x':['mean'],'y':['mean'],'yaw':['mean']}) for datum in df_list]
    df_list_ = [df_[df_['data']['count']>=min_readings] for df_ in df_list_stats]

    df_list_filtered = list()
    for df_ in df_list_:
        if len(df_)>0: df_list_filtered.append(df_)

    if verbose:
        print('Data frames     : {:4d}'.format(len(df_list_filtered)))
        print('Avg Mac/Frame   : {:7.2f}'.format(np.mean(np.asarray([len(df_) for df_ in df_list_filtered]))))       
        print('Avg Reading/Mac : {:7.2f}'.format(np.mean(np.asarray([np.mean(np.asarray(df_['data']['count'])) for df_ in df_list_filtered]))))       

    return df_list_filtered
