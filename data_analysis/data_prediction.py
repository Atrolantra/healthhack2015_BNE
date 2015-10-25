import pandas
import os
import datetime as dt
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import stats
#from ssh_connection import GetDataFromDB
import paramiko

def GetDataFromDB():
    
    users = []
    event_date = []
    event_time = []
    users_cond = []
    relevant_medical = []
    
    ssh_host = '52.64.130.84'
    ssh_user = 'ec2-user'
    ssh_key = 'hh-falls-team.pem'
    
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, username=ssh_user, key_filename=ssh_key)
    
    query = 'mysql -h127.0.0.1 -uhh-falls -p1qaz@WSX falls -e "select ur_no, event_date, event_time from fall_event;"'
    stdin, stdout, stderr = ssh.exec_command(query)
    
    query_1 = 'mysql -h127.0.0.1 -uhh-falls -p1qaz@WSX falls -e "select ur_no from fall_event_client_medical_info;"'
    stdin_, stdout_1, stderr_ = ssh.exec_command(query_1)
    
    query_2 = 'mysql -h127.0.0.1 -uhh-falls -p1qaz@WSX falls -e "select relevant_medical from fall_event_client_medical_info;"'
    stdin_, stdout_2, stderr_ = ssh.exec_command(query_2)
    
    data_frame = stdout.readlines()
    
    users = [str.split(str(data_frame[i]), '\t')[0] for i in range(0,len(data_frame))]
    event_date = [str.split(str(data_frame[i]), '\t')[1] for i in range(0,len(data_frame))]
    event_time = [str.split(str(data_frame[i]), '\t')[2] for i in range(0,len(data_frame))]
    
    users_cond = stdout_1.readlines()
    relevant_medical = stdout_2.readlines()
    
    users = users[1:]
    event_date = event_date[1:]
    event_time = event_time[1:]
    #users_cond = users_cond[1:]
    #relevant_medical = [1:]
    
    #unique_usr = list(set(users))
    #for usr in unique_usr:
    #    indices = [i for i, x in enumerate(users_cond) if x==usr]
    #    relevant_medical = list(relevant_medical_info[ind] for ind in indices)
    
    ssh.close()
    
    return users, event_date, event_time, users_cond, relevant_medical

##os.chdir('/Volumes/Macintosh HD2/My Projects/healthhack2015_BNE')
#data_file = 'falls data.xlsx'
#
#falls_data = pandas.read_excel(data_file,'fall events')
#
## get data info
#date = falls_data['Event_Date']
#t = falls_data['Event_Time']
#users = falls_data['UR_No']

# get medical info matrix
def GetMedicalInfo(relevant_medical, med_index):
    usr_medical_info = []
    
    #if (len(usr_indices) > 0):
    #    for i in usr_indices:
    #        info = relevant_medical[i]
    #        usr_medical_info = str.split(str(info), ',')
    #        usr_medical_info = [x.rstrip() for x in usr_medical_info]
    
    usr_medical_info = str.split(str(relevant_medical[med_index]), ',')
    usr_medical_info = [x.strip() for x in usr_medical_info]
    
    return usr_medical_info
    

# intervals between first and second falls
def fallIntervals(no_fall, usr_evt_interval_dic):
    intervals = []
    for usr in usr_evt_interval_dic.keys():
        if (len(usr_evt_interval_dic[usr]) > (no_fall-1)):
            intervals.append(usr_evt_interval_dic[usr][no_fall-1])
    
    hist_bins = range(0,500,10)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(intervals, hist_bins)
    plt.ylabel('Frequency')
    plt.xlabel('Intervals (day)')
    
    return intervals

# plot number of individual falls
def fallNumber(usr_event_no_dic):
    hist_bins = range(0,20,1)
    fall_no = np.array(usr_event_no_dic.values())
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(fall_no, hist_bins)
    plt.ylabel('Frequency')
    plt.xlabel('No. of Falls')
     
    return fall_no

def CalcRiskPeriod(usr_event_no_dic, usr_evt_interval_dic, usr):
    
    usr_risk_period = 0
    
    if(usr_event_no_dic[usr] >1):
        usr_intervals = fallIntervals(usr_event_no_dic[usr]-1, usr_evt_interval_dic)
        usr_risk_period_dic[usr] = np.array(usr_intervals)

        hist_bins = range(0,500,10)
        distribution = np.histogram(usr_intervals, hist_bins) 
        total = len(usr_intervals)
        evt_percent  = 0.0
        cnt = 0
        sum_evt_no = 0.0
        while (evt_percent <= (0.7) and cnt <= total):
            sum_evt_no = sum_evt_no + distribution[0][cnt]
            evt_percent = sum_evt_no/total
            cnt = cnt + 1
        usr_risk_period = distribution[1][cnt-1]

    return usr_risk_period
    
users, event_date, event_time, users_cond, relevant_medical = GetDataFromDB()

time_stamp = []
datetime_str = []

# get time-stamps of the event time
for i in range(0,len(event_date)):
    dt_str = event_date[i] + ' ' + event_time[i]
    dt_str = dt_str[:-1]
    datetime_str.append(dt_str)
    
    dt_struct = time.strptime(dt_str, "%d/%m/%Y %I:%M %p")
    time_stamp.append(time.mktime(dt_struct))
    
# group event time-stamp of patients
usr_datetime_dic = {}
usr_event_no_dic = {}
usr_evt_interval_dic = {}
usr_evt_interval_avg_dic = {}
usr_evt_interval_std_dic = {}
usr_medical_info_dic = {}
usr_risk_period_dic = {}

for i in range(0, len(users_cond)):
    users_cond[i] = users_cond[i].rstrip()

unique_usr = list(set(users))
for i in range(0, len(unique_usr)):
    usr = unique_usr[i]
    indices = [i for i, x in enumerate(users) if x==usr ]
    indices = np.array(indices)
    event_no = len(indices)
    usr_datetime_dic[usr] = np.array(list(time_stamp[ind] for ind in indices))
    usr_datetime_dic[usr] = np.sort(usr_datetime_dic[usr])
    usr_event_no_dic[usr] = event_no
    usr_evt_interval_dic[usr] = [x/3600/24 for x in np.diff(usr_datetime_dic[usr])]
    if (usr_event_no_dic[usr] > 1):
        usr_evt_interval_avg_dic[usr] = np.mean(np.array(usr_evt_interval_dic[usr]))
        usr_evt_interval_std_dic[usr] = np.std(np.array(usr_evt_interval_dic[usr]))
    else:
       usr_evt_interval_avg_dic[usr] = 0 
       usr_evt_interval_std_dic[usr] = 0
    
    #med_indices = [j for j, x in enumerate(users_cond) if x==usr]
    #med_indices = np.array(med_indices)
    if usr in users_cond:
        med_index = users_cond.index(usr)
        
        usr_medical_info_dic[usr] = len(GetMedicalInfo(relevant_medical, med_index))
        print med_index, usr, relevant_medical[med_index], usr_medical_info_dic[usr]
    else:
        usr_medical_info_dic[usr] = 0   

# calculate risk period                                                    
for i in range(0, len(unique_usr)):
    usr = unique_usr[i]       
    usr_risk_period_dic[usr] = CalcRiskPeriod(usr_event_no_dic, usr_evt_interval_dic, usr)
    
    
# output data

raw_data = {}
raw_data['ur_no'] = unique_usr
raw_data['no_of_falls'] = usr_event_no_dic.values()
raw_data['no_of_pre_conditions'] = usr_medical_info_dic.values()
raw_data['avg_fall_frequency'] = usr_evt_interval_avg_dic.values()
raw_data['high_risk_period'] = usr_risk_period_dic.values()
#raw_data['fall_risk_percent']

df = pandas.DataFrame(raw_data, columns = ['ur_no', 'no_of_falls', 'no_of_pre_conditions','avg_fall_frequency','high_risk_period'])
df.to_csv('output.csv')

