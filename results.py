
import pandas as pd

import glob, os, sys


"""

references:
$ python results.py expes/easyEnergyBudget_3dMid_0.3_energyBud_SHUT_sdscblue_1w_10166421
nb_jobs ctime util avgbsld maxbsld energyWeek energyBudget energyTot jobRun jobRunWithEnd
1197 879651.04 0.48750575961 75.5257410381 5181.72709677 -768815873521.0 -363415525981.0 -1.48171996878e+12 1150 1153.03577247

$ python results.py expes/easyEnergyBudget_3dMid_0.3_energyBud_SHUT_sdscblue_1w_16944036
nb_jobs ctime util avgbsld maxbsld energyWeek energyBudget energyTot jobRun jobRunWithEnd
999 781660.0 0.612596465842 86.9448887136 3566.71733333 86719826643.9 18025040380.7 121788094016.0 962 966.102231525

"""


def utilization(df, measure='requested_number_of_processors', measure_name="util", queue=False):
    
    if queue:
        begin_col = "submission_time"
        end_col = "starting_time"
    else:
        begin_col = "starting_time"
        end_col = "finish_time"
    
    startu = pd.DataFrame([df[begin_col], df[measure]]).transpose()
    startu.columns = ['time', measure_name]


    endu = pd.DataFrame([df[end_col], -df[measure]]).transpose()
    endu.columns = ['time', measure_name]


    u = startu.append(endu)


    u = u.groupby(['time']).sum()
    u = u[u[measure_name] !=0]
    u[measure_name] = u[measure_name].cumsum()

    return u



def jobs_in_queue_at(df, t):
    return df[ (df.submission_time <= t) & (t <= df.starting_time)]
def jobs_running_at(df, t):
    return df[ (df.starting_time <= t) & (t <= df.finish_time)]



from itertools import tee, izip
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)



dir_csv = sys.argv[1]

if "curie" in dir_csv:
    tot_procs = 80640
elif "metacentrum" in dir_csv:
    tot_procs = 3356
elif "sdscblue" in dir_csv:
    tot_procs = 1152
else:
    print "ERROR!"
    exit()

job_csv = dir_csv+"/out_jobs.csv"
df = pd.read_csv(job_csv)

pstate_csv = dir_csv+"/out_pstate_changes.csv"
dfp = pd.read_csv(pstate_csv)

# On some simulations, batsim bugs and don't report changing state in dfp
# we add them mannually
time_to_boot = 151
time_to_shut = 6
if len(dfp.new_pstate.unique()) == 2:
    for (i, r) in dfp.iterrows():
        if r["new_pstate"] == 0:#in idle state
            if r["time"] - time_to_boot >= 0:
                dfp.loc[len(dfp)] = [r["time"] - time_to_boot, r["machine_id"], 15]
        elif r["new_pstate"] == 13:#in shut state
            dfp.loc[len(dfp)] = [r["time"] - time_to_shut, r["machine_id"], 14]

    dfp = dfp.sort_values(by=["time","new_pstate"])


dfss = df[df.starting_time < 3600*24*7]
jobRun = len(dfss[dfss.finish_time < 3600*24*7])
dfssl = dfss[dfss.finish_time >= 3600*24*7]
jobRunWithEnd = jobRun+sum((3600*24*7 - dfssl.starting_time)/dfssl.execution_time)
#print jobRun, jobRunWithEnd



#nb_jobs
nb_jobs = len(df.jobID)

#ctime
ctime = df.finish_time.max()-df.submission_time.min()

#util
#utilFull = sum(df.requested_number_of_processors*df.execution_time)/ctime/80640


utilt = utilization(df)
utilt_week = utilt[utilt.index <= 3600*24*7]
util = utilt_week.util.mean()/tot_procs


#import matplotlib.pyplot as plt
#plt.step(utilt.index, utilt.util)
#plt.show()


#bsld
df['ten'] = 10.0
df['one'] = 1.0

df['bsld'] = (df.execution_time+df.waiting_time)/df[['ten', 'execution_time']].max(axis=1)

df['bsld'] = df[['one', 'bsld']].max(axis=1)

avgbsld = df.bsld.mean()
maxbsld = df.bsld.max()



#energy_consumed in period


machines = range(0, tot_procs)
mcurstate = {}
cur_time = 0
m_idle = len(machines)
m_shutting = 0
m_down = 0
m_booting = 0

machines_state = pd.DataFrame(columns=('time', 'idle', 'shutting', 'down', 'booting'))

for m in machines:
    mcurstate[m] = 0
for (i, r) in dfp.iterrows():
    if type(r["machine_id"]) is str and "-" in r["machine_id"]:
        m = r["machine_id"].split("-")
        machine_id_from = int(m[0])
        machine_id_to = int(m[1])
    else:
        machine_id_from = int(r["machine_id"])
        machine_id_to = int(r["machine_id"])
    
    machines_id = [x for x in range(machine_id_from, machine_id_to+1) if mcurstate[x] != r["new_pstate"]]
    if len(machines_id) == 0:
        continue

    if r["time"] != cur_time:
        machines_state.loc[len(machines_state)] = [cur_time, m_idle, m_shutting, m_down, m_booting]
    cur_time = r["time"]
    
    old_pstate = mcurstate[machines_id[0]]
    assert not sum([mcurstate[x] != old_pstate for x in machines_id])
    
    if r["new_pstate"] == 0:
        m_booting -= len(machines_id)
        m_idle += len(machines_id)
    if r["new_pstate"] == 14:
        m_idle -= len(machines_id)
        m_shutting += len(machines_id)
    if r["new_pstate"] == 13:
        m_shutting -= len(machines_id)
        m_down += len(machines_id)
    if r["new_pstate"] == 15:
        m_down -= len(machines_id)
        m_booting += len(machines_id)
    
    for machine_id in machines_id:
        mcurstate[machine_id] = r["new_pstate"]

if len(machines_state) == 0:
    machines_state.loc[len(machines_state)] = [0, len(machines), 0, 0, 0]

machines_state = machines_state.set_index("time")


power_idle = 95.0
power_shutting = 616.08/6.1
power_down = 9.75
power_booting = 18966.4228/151.52


df['powerCompute'] = df.consumed_energy/df.execution_time
e = utilization(df, measure='powerCompute', measure_name="powerCompute")

#merge
utilAll = pd.concat([e['powerCompute'], utilt['util'], machines_state], axis=1)
for i in utilAll.columns:
    utilAll[i] = utilAll[i].fillna(method='ffill')


utilAll['power'] = utilAll.powerCompute + (utilAll.idle - utilAll.util)*power_idle + utilAll.shutting*power_shutting + utilAll.booting*power_booting+utilAll.down*power_down




if "1dMid" in job_csv:
	start_time = 3600*24*3
	end_time = 3600*24*4
elif "3dMid" in job_csv:
	start_time = 3600*24*2
	end_time = 3600*24*5
else:
	start_time = 0
	end_time = 0

if not(start_time in utilAll.index):
    utilAll.loc[start_time] = utilAll.loc[utilAll[utilAll.index < start_time].index.max()]
if not(end_time in utilAll.index):
    utilAll.loc[end_time] = utilAll.loc[utilAll[utilAll.index < end_time].index.max()]

utilAll = utilAll.sort_index()

#utilAll = utilAll[utilAll.index >= start_time]
#utilAll = utilAll[utilAll.index <= end_time]

energyWeek = 0.0
energyBudget = 0.0
energyTot = 0.0
for (i1, row1), (i2, row2) in pairwise(utilAll.iterrows()):
    if 0 <= i1 and i2 <= 3600*24*7:
        energyWeek += (i2-i1)*row1["power"]
    if start_time <= i1 and i2 <= end_time:
        energyBudget += (i2-i1)*row1["power"]
    energyTot += (i2-i1)*row1["power"]






print "nb_jobs", "ctime", "util", "avgbsld", "maxbsld", "energyWeek", "energyBudget", "energyTot", "jobRun", "jobRunWithEnd"
print nb_jobs, ctime, util, avgbsld, maxbsld, energyWeek, energyBudget, energyTot, jobRun, jobRunWithEnd

