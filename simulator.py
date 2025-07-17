import argparse
from ProcessTrace import ProcessTrace


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Cache simulator input parameters")
    parser.add_argument("-file","--trace_file", type=str, help="Trace file", required=True)
    parser.add_argument("-ns","--num_sets", type=int, help="Number of sets in cache", required=True)
    parser.add_argument("-nw","--num_ways", type=int, help="Number of ways for associativity", required=True)
    parser.add_argument("-ls","--line_size", type=int, help="Size of each cache line", required=True)
    parser.add_argument("-rp","--replacement_policy", type=int, help="Size of each cache line. Pass 0 for LRU, 1 for 1-bit LRU", required=True)
    args = parser.parse_args()
    num_sets = args.num_sets
    num_ways = args.num_ways
    line_size = args.line_size
    trace_file = args.trace_file
    replacement_policy = args.replacement_policy
    def is_power2(num):
        return ((num & (num - 1)) == 0) and num != 0

    if not is_power2(num_sets):
        raise Exception("The number of sets input should be a power of 2")
    if num_ways > 8:
        raise Exception("The number of ways input should not be greater than 8")
    if not is_power2(num_ways):
        raise Exception("The number of ways input should be a power of 2")
    if not 32 <= line_size <= 128:
        raise Exception("The size of cache line should is not in the specified range")
    if not is_power2(line_size):
        raise Exception("The size of cache line should be a power of 2")
    if replacement_policy not in [0, 1]:
        raise Exception("Replacement policy should be either 0 or 1")

    input_parameters = [num_sets, num_ways, line_size, replacement_policy]
    ProcessTrace(trace_file, input_parameters)
