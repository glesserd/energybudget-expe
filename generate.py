
import os, json, copy
import glob




schedulers = []







schedulers += [{
        "name_expe": "easyBackfill",
        "name": "easyBackfill",
        "verbosity":10,
        "protection":True,
        "options": {}
        }]





budgets = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 100.0/203.12, 0.3]

name_allow = {}
name_allow[(True, False)] = "energyBud"
name_allow[(True, True)] = "reducePC"
name_allow[(False, True)] = "PC"
name_allow[(False, False)] = "SHIT"

name_shut = {}
name_shut[True] = "SHUT"
name_shut[False] = "IDLE"

schedulers += [{
        "name_expe": "easyEnergyBudget_3dMid_"+str(b)+"_"+name_allow[allow]+"_"+name_shut[shut],
        "name":"easyEnergyBudget",
        "verbosity":10,
        "protection":True,
        "options": {
            "budget_total": b*80640*203.12*3600*24*3,
            "budget_start": 2*24*3600,
            "budget_end": 5*24*3600,
            "allow_FCFS_jobs_to_use_budget_saved_measured": allow[0],
            "reduce_powercap_to_save_energy": allow[1],
            "monitoring_period":10*60,
            "power_idle": 100.0,
            "power_compute": 203.12,
            "opportunist_shutdown": shut,
            "pstate_switchon": 0,
            "pstate_switchoff": 13,
            "timeto_switchoff": 10,
            "timeto_switchon": 200
            }
        } for b in budgets for allow in [(True, False), (True, True), (False, True)] for shut in [True,False]]





workloads_to_use = glob.glob("traces/curie_*.json")

options = [{
    "platform":"../../platforms/cluster80640_energy.xml",
    "workload": "EXPE/"+w,
    "output_dir":"SELF",#where all output files (stdins, stderrs, csvs...) will be outputed.
                        #if set to "SELF" then output on the same dir as this option file.
    "batsim": {
        "export":"out",# The export filename prefix used to generate simulation output
        "energy-plugin": True,#        Enables energy-aware experiments
        "disable-schedule-tracing": True,#remove paje output
        "verbosity": "quiet"  #Sets the Batsim verbosity level. Available values
                                    # are : quiet, network-only, information (default), debug.
        },
    "scheduler": copy.deepcopy(s)
    } for s in schedulers for w in workloads_to_use]





for opt in options:
    opt["scheduler"]["name_expe"] += "_"+os.path.splitext(os.path.basename(opt["workload"]))[0]
    
    new_dir = "expes/"+opt["scheduler"]["name_expe"]
    print new_dir
    try:
        os.mkdir(new_dir)
    except OSError:
        print "ALREADY HERE"
        pass
    #print json.dumps(opt, indent=4)
    open(new_dir+'/expe.json','w').write(json.dumps(opt, indent=4))


