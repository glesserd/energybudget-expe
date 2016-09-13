
EXPE_FOLDERS := $(wildcard expes/*)
SIMULS_OUT := $(patsubst %,%/out_jobs.csv,$(EXPE_FOLDERS))

WORKLOADS_SWF := $(wildcard traces/*.swf)
WORKLOADS_JSON := $(patsubst %.swf,%.json,$(WORKLOADS_SWF))

OBJECTIVES_OUT := $(patsubst %,%/objectives.csv,$(EXPE_FOLDERS))


all:


swf2json: $(WORKLOADS_JSON)

%.json:
	python ../../../../expe-batsim/swfToJsonConverter.py -i 0 -cpu 100e6 -com 0.0 -jg 2 -pf 80640 --keepOriginalId $*.swf $@


# program_OBJS := $(foreach tra,$(TRACES_IN),$(foreach s,$(SCHED),$(tra)_$(s).o))
generate: swf2json
	python generate.py


simuls: $(SIMULS_OUT)

%/out_jobs.csv:
	cd ..;python launch_expe.py EXPE/$*/expe.json
# 	echo "faire qqch avec $*/expe.json et le mettre dans $@"


objectives: $(OBJECTIVES_OUT)
%/objectives.csv:
	python results.py $* > $*/objectives.csv
