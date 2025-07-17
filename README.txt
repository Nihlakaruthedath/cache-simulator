Usage: python simulator.py <Input Parameters>

Parameters usage: 
Cache simulator input parameters [-h] [-file TRACE_FILE] [-ns NUM_SETS] [-nw NUM_WAYS] [-ls LINE_SIZE] [-rp REPLACEMENT_POLICY]

optional arguments:
  -h, --help            show this help message and exit
  -file TRACE_FILE, --trace_file TRACE_FILE
                        Trace file
  -ns NUM_SETS, --num_sets NUM_SETS
                        Number of sets in cache
  -nw NUM_WAYS, --num_ways NUM_WAYS
                        Number of ways for associativity
  -ls LINE_SIZE, --line_size LINE_SIZE
                        Size of each cache line
  -rp REPLACEMENT_POLICY, --replacement_policy REPLACEMENT_POLICY
                        Size of each cache line. Pass 0 for LRU, 1 for 1-bit LRU
						
Example
--------
		python simulator.py -file test.txt -ns 128 -nw 2 -ls 64 -rp 1
		python simulator.py --trace_file test.txt --num_sets 128 --num_ways 2 --line_size 64 --replacement_policy 1