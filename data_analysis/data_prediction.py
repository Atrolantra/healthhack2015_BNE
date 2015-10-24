import pandas
import os
import datetime as dt
import time
import numpy as np
import matplotlib.pyplot as plt

#os.chdir('/Volumes/Macintosh HD2/My Projects/healthhack2015_BNE')
data_file = 'falls data.xlsx'

falls_data = pandas.read_excel(data_file,'fall events')

time_stamp = []

# get data info
date = falls_data['Event_Date']
t = falls_data['Event_Time']
users = falls_data['UR_No']
dt_str = date + ' ' + t

# get time-stamps of the event time
for i in range(0,len(date)):
    dt_struct = time.strptime(dt_str[i], "%d/%m/%Y %I:%M %p")
    time_stamp.append(time.mktime(dt_struct))
    
# group event time-stamp of patients
usr_datetime_dic = {}
usr_time_dic = {}
usr_event_no_dic = {}
usr_evt_interval_dic = {}

unique_usr = list(set(users))
for i in range(0, len(unique_usr)):
    usr = unique_usr[i]
    indices = [i for i, x in enumerate(users) if x==usr ]
    indices = np.array(indices)
    event_no = len(indices)
    usr_datetime_dic[usr] = np.array(list(time_stamp[ind] for ind in indices))
    usr_datetime_dic[usr] = np.sort(usr_datetime_dic[usr])
    usr_time_dic[usr] = list(t[ind] for ind in indices)
    usr_event_no_dic[usr] = event_no
    usr_evt_interval_dic[usr] = [x/3600/24 for x in np.diff(usr_datetime_dic[usr])]

# intervals between first and second falls
def fallIntervals(no_fall, usr_evt_interval_dic):
    intervals = []
    for usr in unique_usr:
        if (len(usr_evt_interval_dic[usr]) > (no_fall-1)):
            intervals.append(usr_evt_interval_dic[usr][no_fall-1])
    
    hist_bins = range(0,500,10)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(intervals, hist_bins)
    plt.ylabel('Frequency')
    plt.xlabel('Intervals (day)')
    
    return intervals

# plot individual fall interval
