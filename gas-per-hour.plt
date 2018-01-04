set term png size 1280,1024 enhanced
set grid
set title "Gas usage per hour"

set timefmt "%Y-%m-%d %H:%M"
set xdata time
set xrange [ "2018-01-01 00:00":]

set timefmt "%s"
set format x "%b %d\n%H:%M"
set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
set boxwidth 0.9

set xlabel "Time in UTC"
set ylabel "Gas in m^3"

set boxwidth 1800 absolute # per hour

plot 'values-per-hour.csv' using 1:2 with boxes title 'gas'
