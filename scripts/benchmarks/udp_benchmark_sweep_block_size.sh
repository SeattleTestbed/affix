#!/bin/bash
for i in 1 4 16 64 256 1024 4096 16384  
do 
    echo "Starting block size: $i"
    echo -e "Data block size: $i" >> python_udp_benchmark.out
    python affix_python_udp_nonblock_benchmark.py $i 64 >> python_udp_benchmark.out
    echo -e "\n\n" >> python_udp_benchmark.out

    echo -e "Data block size: $i" >> repy_udp_benchmark.out
    python affix_repy_udp_benchmark.py $i 64 >> repy_udp_benchmark.out
    echo -e "\n\n" >> repy_udp_benchmark.out
done