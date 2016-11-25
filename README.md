
# Energy budget paper

This repository contains the scripts to produce the results of the energy budget paper.
The full name of the paper and the co-athors are not given yet, as it is not published yet.

Most of the things are automatic thank to the magic of the Makefile.

## Simulator

We use the [Batsim simulator](https://github.com/oar-team/batsim) . Clone it, compile it and install it.
The algorithms used in the paper are within the simulator, as python scripts. Take a look at [this](https://github.com/oar-team/batsim/blob/master/schedulers/pybatsim/schedulers/easyEnergyBudget.py) file.

In the following of this file, we assume that this repository has been cloned in `schedulers/pybatsim/schedulers/EXPE` directory of batsim.

## Start simulations

First generate the json files discribing each experiment by running:
```
python generate.py
python generate_sdscblue.py
python generate_metacentrum.py
```
Then, you can start the simulation:
```
make simuls
```
Don't forget the `-j` option of `make` to run multiple simulations at once.
It tooks me 2 weeks to run everything on an old 256 cores machine (`-j 256`).

You can determine the progress of the simulations using:
```
echo "Simulations ended: " $(( $(ls expes/*/out_jobs* |wc -l) *100 / $(ls expes/ |wc -l))) "%"
```

## Compute results
Once the simulations are finished:
```
make results
```
This can also take quite a long time (about 1 day for me).

## Display results

```
jupyter-notebook
```
Then, open TestnewMC.ipynb and rerun each nodes.



