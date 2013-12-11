reset
set term postscript portrait enhanced color "Times-Roman" 22
set size 2,1
set output "tcp_udp_benchmark.ps"


set title "Benchmark of UDP Communication over Localhost\nFor Both Python and Repy"

set xtics rotate by -45
set xtics font ",16"


set key top left width 1
set xlabel "Throughput (KBytes/s)"
set ylabel "API type"

set boxwidth 0.3
set style fill solid

plot 'tcp_udp_benchmark_average.out' using 2:xtic(1) with boxes notitle,\
     'tcp_udp_benchmark_average.out' using 0:($2+1000):($2) with labels notitle