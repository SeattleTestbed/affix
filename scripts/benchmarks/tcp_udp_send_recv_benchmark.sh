#!/bin/bash

for i in {1..10}
do
    echo -e "Python TCP nonblock."
    val=`python affix_python_tcp_nonblock_benchmark.py 1024 256 | grep -i throughput`
    echo -e "Python TCP nonblock: $val" >> tcp_udp_recv_send_bench.out
    
    echo -e "Python TCP recv/repy send."
    val=`python affix_python_tcp_recv_repy_send_benchmark.py 1024 256 | grep -i throughput`
    echo -e "Python TCP recv/repy send: $val" >> tcp_udp_recv_send_bench.out
    
    
    echo -e "Python TCP send/repy recv." 
    val=`python affix_python_tcp_send_repy_recv_benchmark.py 1024 256 | grep -i throughput`
    echo -e "Python TCP send/repy recv: $val" >> tcp_udp_recv_send_bench.out
    
    echo -e "Repy TCP nonblock." 
    val=`python affix_repy_tcp_benchmark.py 1024 256 | grep -i throughput`
    echo -e "Repy TCP nonblock: $val" >> tcp_udp_recv_send_bench.out
    
    echo -e "Python UDP nonblock."
    val=`python affix_python_udp_nonblock_benchmark.py 1024 256 | grep -i throughput`
    echo -e "Python UDP nonblock: $val" >> tcp_udp_recv_send_bench.out
    
    echo -e "Python UDP recv/repy send nonblock."
    val=`python affix_python_udp_recv_repy_send_benchmark.py 1024 256 | grep -i throughput`
    echo -e "Python UDP recv/repy send nonblock: $val" >> tcp_udp_recv_send_bench.out
    
    echo -e "Python UDP send/repy recv nonblock." 
    val=`python affix_python_udp_send_repy_recv_benchmark.py 1024 256 | grep -i throughput`
    echo -e "Python UDP send/repy recv nonblock: $val" >> tcp_udp_recv_send_bench.out
    
    echo -e "Repy UDP nonblock."
    val=`python affix_repy_udp_benchmark.py 1024 256 | grep -i throughput`
    echo -e "Repy UDP nonblock: $val" >> tcp_udp_recv_send_bench.out
done