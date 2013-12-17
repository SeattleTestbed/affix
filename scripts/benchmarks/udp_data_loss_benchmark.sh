#!/bin/bash

for i in 0.1 0.01 0.001 0.0001 0.00001 0.000001 0.0000001 0.00000001
do    
    echo -e "Python UDP nonblock."
    val=`python affix_python_udp_nonblock_benchmark.py 1024 256 | grep -i "Loss rate"`
    echo -e "Python UDP nonblock: $val" >> udp_data_loss_benchmark.out
    
    echo -e "Python UDP recv/repy send nonblock."
    val=`python affix_python_udp_recv_repy_send_benchmark.py 1024 256 | grep -i "Loss rate"`
    echo -e "Python UDP recv/repy send nonblock: $val" >> udp_data_loss_benchmark.out
    
    echo -e "Python UDP send/repy recv nonblock." 
    val=`python affix_python_udp_send_repy_recv_benchmark.py 1024 256 | grep -i "Loss rate"`
    echo -e "Python UDP send/repy recv nonblock: $val" >> udp_data_loss_benchmark.out
    
    echo -e "Repy UDP nonblock."
    val=`python affix_repy_udp_benchmark.py 1024 256 | grep -i "Loss rate"`
    echo -e "Repy UDP nonblock: $val" >> udp_data_loss_benchmark.out
done