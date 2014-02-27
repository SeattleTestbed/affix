#!/bin/bash

for size in 40 1500 65000
do

for i in {1..10}
do
    echo -e "Python TCP nonblock."
    val=`python affix_python_tcp_nonblock_benchmark.py $size 100 12346 12346 | grep -i throughput`
    echo -e "Python TCP nonblock, Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out
    
    echo -e "Python TCP recv/repy send."
    val=`python affix_python_tcp_recv_repy_send_benchmark.py $size 100 | grep -i throughput`
    echo -e "Python TCP recv/repy send, Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out
    
    echo -e "Python TCP send/repy recv." 
    val=`python affix_python_tcp_send_repy_recv_benchmark.py $size 100 | grep -i throughput`
    echo -e "Python TCP send/repy recv, Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out
    
    echo -e "Repy TCP nonblock." 
    val=`python affix_repy_tcp_benchmark.py $size 100 | grep -i throughput`
    echo -e "Repy TCP nonblock, Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out

    echo -e "Repy TCP Noop Affix (Native)." 
    val=`python affix_repy_tcp_noop_benchmark.py $size 100 12347 12347 '(NoopAffix)' | grep -i throughput`
    echo -e "Repy TCP Noop Affix (Native), Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out

    echo -e "Repy TCP Coordination Affix." 
    val=`python affix_repy_tcp_noop_benchmark.py $size 100 12348 12348 '(CoordinationAffix)' | grep -i throughput`
    echo -e "Repy TCP Coordination Affix (Native), Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out
    

    echo -e "Repy TCP Noop Affix (Proxy)." 
    val=`python affix_python_tcp_nonblock_benchmark.py $size 100 12346 12345 '(NoopAffix)' | grep -i throughput`
    echo -e "Repy TCP Noop Affix (Proxy), Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out
done
done

exit
    
if [1 -eq 0]; then
    echo -e "Python UDP nonblock."
    val=`python affix_python_udp_nonblock_benchmark.py $size 100 | grep -i throughput`
    echo -e "Python UDP nonblock, Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out

    echo -e "Python UDP recv/repy send nonblock."
    val=`python affix_python_udp_recv_repy_send_benchmark.py $size 100 | grep -i throughput`
    echo -e "Python UDP recv/repy send nonblock, Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out
    
    echo -e "Python UDP send/repy recv nonblock." 
    val=`python affix_python_udp_send_repy_recv_benchmark.py $size 100 | grep -i throughput`
    echo -e "Python UDP send/repy recv nonblock, Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out
    
    echo -e "Repy UDP nonblock."
    val=`python affix_repy_udp_benchmark.py $size 100 | grep -i throughput`
    echo -e "Repy UDP nonblock, Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out

    echo -e "Repy UDP Noop Affix (Native)."
    val=`python affix_repy_udp_noop_benchmark.py $size 100 12345 12345 '(NoopAffix) | grep -i throughput`
    echo -e "Repy UDP Noop Affix (Native), Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out

    echo -e "Repy UDP Coordination Affix."
    val=`python affix_repy_udp_noop_benchmark.py $size 100 12345 12345 '(CoordinationAffix) | grep -i throughput`
    echo -e "Repy UDP Noop Affix (Native), Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out

    echo -e "Repy UDP Noop Affix (Proxy)."
    val=`python affix_repy_udp_noop_benchmark.py $size 100 12346 12345 '(NoopAffix) | grep -i throughput`
    echo -e "Repy UDP Noop Affix (Proxy), Block size: $size Throughput: $val" >> tcp_udp_recv_send_bench.out
fi