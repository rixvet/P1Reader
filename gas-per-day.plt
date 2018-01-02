set term png size 1280,1024 enhanced
set grid
set title "Gas usage per day"
set xdata time
set timefmt "%s"
set format x "%b %d\n%H:%M"
set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
set boxwidth 0.9

set boxwidth 43200 absolute # per day

plot 'values-per-day.csv' using 1:2 with boxes title 'gas in m^3'
#
