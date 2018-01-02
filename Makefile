all: sync parse graph
update: sync parse

sync:
	rsync -av 'homepi:~/P1_DATA_20*_*.csv' .
parse:
	$(eval TMP := $(shell echo ./P1_DATA_$$(date -d '1 month ago' '+%Y_%m').csv ./P1_DATA_$$(date '+%Y_%m').csv))
	./landis_gys_e350.py --bucket_size 3600 parse ${TMP} > values-per-hour.csv	
	./landis_gys_e350.py --bucket_size 86400 parse ${TMP} > values-per-day.csv	
graph:
	gnuplot gas-per-hour.plt > gas_per_hour.png
	gnuplot gas-per-day.plt > gas_per_day.png
	

