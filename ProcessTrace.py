#from _ast import Pass
ADDRESS_BITS = 32
import math
from collections import deque
import copy

class ProcessTrace:
    """
    Class used to process the access trace to the cache
    """
    def __init__(self, trace_file, input_parameters):
        self.trace_file = trace_file
        self.num_sets = input_parameters[0]
        self.num_ways = input_parameters[1]
        self.line_size = input_parameters[2]
        self.replacement_policy = input_parameters[3]
        self.cache_hits = 0
        self.cache_misses = 0
        self.evictions = 0
        self.write_backs = 0
        self._initialize()

    def _initialize(self):
        """
        Initialize parameters needed to process the trace
        :return: None
        """
        self.cache_dict = {}  # Valid bit, dirty bit, tag bits, set bits
        file = open(self.trace_file, "r")
        self.data = file.read()
        self.access_list = self.data.split("\n")# TODO: Try to avoid taking empty lines from the file
        set_select_bits = self.decimal_to_binary(self.num_sets) #len(self.decimal_to_binary(self.num_sets))-1
        byte_select_bits = self.decimal_to_binary(self.line_size)#len(self.decimal_to_binary(self.line_size))-1
        self.byte_select_range = (ADDRESS_BITS - byte_select_bits, ADDRESS_BITS)
        self.set_select_range = (ADDRESS_BITS - byte_select_bits - set_select_bits, self.byte_select_range[0])
        self.tag_select_range = (0, self.set_select_range[0])
        self.cache_dict = dict((item, ['0', '0', '0']) for item in self.generate_binary(self.num_sets))
        self.process_trace()
        self.print_calculations()

    def print_calculations(self):
        """
        Display the output values
        :return: None
        """
        read_access_counter = 0
        write_access_counter = 0
        invalidate_access_counter = 0
        print("Total number of cache accesses: ", len(self.access_list))
        for item in self.access_list:
            access_type = item.split(' ')[0].strip()
            if access_type == '0':
                read_access_counter = read_access_counter + 1
            elif access_type == '1':
                write_access_counter = write_access_counter + 1
            elif access_type == '2':
                invalidate_access_counter = invalidate_access_counter + 1
            else:
                raise Exception("Invalid access type for an entry in the trace")

        print("Number of cache reads: ", read_access_counter)
        print("Number of cache writes: ", write_access_counter)
        print("Number of invalidates: ", invalidate_access_counter)
        print("Number of cache hits: ", self.cache_hits)
        print("Number of cache misses: ", self.cache_misses)
        print("Cache hit ratio: {0:.2f}%".format(100*self.cache_hits/(self.cache_hits+self.cache_misses)))
        print("Cache miss ratio: {0:.2f}%".format(100*self.cache_misses/(self.cache_hits+self.cache_misses)))
        print("Number of evictions: ", self.evictions)
        print("Number of write backs: ", self.write_backs)

    def process_trace(self):
        """
        Call the respective function for direct mapped cache or in case of associativity true lru or 1-bit lru
        :return: None
        """
        if self.num_ways == 1:
            #self.process_direct_mapped_cache()
            self.process_direct_mapped_cache_new2()
        else:
            if self.replacement_policy == 0:
                self.process_true_lru_cache()
            else:
                #self.process_1_bit_lru_cache()
                self.process_1_bit_lru_cache_new1()
    def process_direct_mapped_cache_new(self):
        #print("In process_true_lru_cache")
        #associativity=self.num_ways
        self.LRU_Cache_dict = dict((item,{}) for item in self.generate_binary(self.num_sets))
        for item in self.access_list:
            access_type = int(item.split(' ')[0])
            address = self.hex_to_binary(item.split(' ')[1])
            item_index = address[self.set_select_range[0]:self.set_select_range[1]]
            tag_bits = address[self.tag_select_range[0]:self.tag_select_range[1]].strip()
            if item_index in self.LRU_Cache_dict.keys():
                if access_type != 2 and tag_bits not in self.LRU_Cache_dict[item_index].keys():
                    if access_type == 0 :
                        self.LRU_Cache_dict[item_index][tag_bits]=['1','0']
                        self.cache_misses += 1
                    elif access_type == 1:
                        self.LRU_Cache_dict[item_index][tag_bits]=['1','1']
                        self.cache_misses += 1
                    else:
                        print("### Code ERROR 1 ### {} {} {} ".format(access_type,tag_bits,item_index))
                elif tag_bits in self.LRU_Cache_dict[item_index].keys():
                    if access_type == 0 and self.LRU_Cache_dict[item_index][tag_bits][0] == '1':
                        self.LRU_Cache_dict[item_index][tag_bits][0]='1'
                        self.cache_hits += 1
                    elif access_type == 1 and self.LRU_Cache_dict[item_index][tag_bits][0] == '1':
                        self.LRU_Cache_dict[item_index][tag_bits][0]='1'
                        self.LRU_Cache_dict[item_index][tag_bits][1]='1'
                        self.cache_hits += 1
                    elif access_type == 2:
                        if self.LRU_Cache_dict[item_index][tag_bits][1] == '1':     # cache not fill, same tagbits
                            self.write_backs += 1
                        self.evictions += 1
                        self.LRU_dict[item_index].remove(tag_bits)
                    else:
                        print("### Code ERROR 2 ###") 
                        
    def process_direct_mapped_cache_new2(self):
        #print("In process_true_lru_cache")
        associativity=1
        self.LRU_Cache_dict = dict((item,{}) for item in self.generate_binary(self.num_sets))
        self.LRU_dict = dict((item,deque(maxlen=associativity)) for item in self.generate_binary(self.num_sets))
        for item in self.access_list:
            access_type = int(item.split(' ')[0])
            address = self.hex_to_binary(item.split(' ')[1])
            item_index = address[self.set_select_range[0]:self.set_select_range[1]]
            tag_bits = address[self.tag_select_range[0]:self.tag_select_range[1]].strip()
            
            if item_index in self.LRU_Cache_dict.keys():
                if len(self.LRU_Cache_dict[item_index]) < associativity  and access_type != 2 and tag_bits not in self.LRU_Cache_dict[item_index].keys(): 
                    if access_type == 0:
                        self.LRU_Cache_dict[item_index][tag_bits]=['1','0'] #adding key tag-bits and assigning valid and dirty bit as a list
                        self.LRU_dict[item_index].appendleft(tag_bits)
                        self.cache_misses += 1
                    elif access_type == 1:
                          self.LRU_Cache_dict[item_index][tag_bits]=['1','1']
                          self.LRU_dict[item_index].appendleft(tag_bits)
                          self.cache_misses += 1
                    #else:
                     #   print("### Code ERROR 1 ### {} {} {} ".format(access_type,tag_bits,item_index))
                elif len(self.LRU_Cache_dict[item_index]) < associativity and access_type != 2 and tag_bits in self.LRU_Cache_dict[item_index].keys(): #repeated data before cache fill
                    if access_type == 0 and self.LRU_Cache_dict[item_index][tag_bits][0] == '1':
                        self.LRU_Cache_dict[item_index][tag_bits][0]='1'
                        self.cache_hits += 1
                        
                    elif access_type == 1 and self.LRU_Cache_dict[item_index][tag_bits][0] == '1':
                        self.LRU_Cache_dict[item_index][tag_bits][0]='1'
                        self.LRU_Cache_dict[item_index][tag_bits][1]='1'
                        self.cache_hits += 1
                    self.LRU_dict[item_index].remove(tag_bits)
                    self.LRU_dict[item_index].appendleft(tag_bits)
                    
                elif len(self.LRU_Cache_dict[item_index]) < associativity and access_type == 2 and tag_bits in self.LRU_Cache_dict[item_index].keys():     # Increasing cache Hit.
                    if self.LRU_Cache_dict[item_index][tag_bits][1] == '1':     # cache not fill, same tagbits
                        self.write_backs += 1
                    del self.LRU_Cache_dict[item_index][tag_bits]
                    self.evictions += 1
                    self.LRU_dict[item_index].remove(tag_bits) 
                      
                elif len(self.LRU_Cache_dict[item_index]) == associativity  and tag_bits in self.LRU_Cache_dict[item_index].keys():
                    if access_type == 0:
                        self.cache_hits += 1
                        self.LRU_Cache_dict[item_index][tag_bits][0]='1' 
                        self.LRU_dict[item_index].remove(tag_bits)
                        self.LRU_dict[item_index].appendleft(tag_bits)
                    elif access_type == 1:
                        self.LRU_Cache_dict[item_index][tag_bits][0]='1'
                        self.LRU_Cache_dict[item_index][tag_bits][1]='1'
                        self.cache_hits += 1
                        self.LRU_dict[item_index].remove(tag_bits)
                        self.LRU_dict[item_index].appendleft(tag_bits)
                    elif access_type == 2:
                        if self.LRU_Cache_dict[item_index][tag_bits][1] == '1':
                           self.write_backs += 1
                        del self.LRU_Cache_dict[item_index][tag_bits]
                        self.evictions += 1
                        self.LRU_dict[item_index].remove(tag_bits)
                        
                elif len(self.LRU_Cache_dict[item_index]) == associativity  and tag_bits not in self.LRU_Cache_dict[item_index].keys():
                    if access_type == 0 or access_type == 1:
                        evict_TagBit =  self.LRU_dict[item_index].pop()
                        if self.LRU_Cache_dict[item_index][evict_TagBit][1] == '1':
                           self.write_backs += 1
                        del self.LRU_Cache_dict[item_index][evict_TagBit]
                        if access_type == 0:
                           self.LRU_Cache_dict[item_index][tag_bits] = ['1','0']
                        elif access_type == 1:
                            self.LRU_Cache_dict[item_index][tag_bits] = ['1','1']
                        self.LRU_dict[item_index].appendleft(tag_bits)
                        self.cache_misses += 1
                        self.evictions += 1
                    #if access_type == 2:
                        #print("#### No such address existing to invalidate, So nothing to do") 
                if len(self.LRU_Cache_dict[item_index]) > associativity:
                    print("### ERROR - Cache dic is more then associativity")
                #else:
                    #print("### Code ERROR 2 #### {} {} {}".format(access_type,tag_bits,self.LRU_Cache_dict[item_index].keys()))
            #else:
                #print("Cache Index not present in self.LRU_Cache_dict, ERROR!! WRONG ACCESS!!!")

    def process_true_lru_cache(self):
        #print("In process_true_lru_cache")
        associativity=self.num_ways
        self.LRU_Cache_dict = dict((item,{}) for item in self.generate_binary(self.num_sets))
        self.LRU_dict = dict((item,deque(maxlen=associativity)) for item in self.generate_binary(self.num_sets))
        for item in self.access_list:
            access_type = int(item.split(' ')[0])
            address = self.hex_to_binary(item.split(' ')[1])
            item_index = address[self.set_select_range[0]:self.set_select_range[1]]
            tag_bits = address[self.tag_select_range[0]:self.tag_select_range[1]].strip()
            
            if item_index in self.LRU_Cache_dict.keys():
                if len(self.LRU_Cache_dict[item_index]) < associativity  and access_type != 2 and tag_bits not in self.LRU_Cache_dict[item_index].keys(): 
                    if access_type == 0:
                        self.LRU_Cache_dict[item_index][tag_bits]=['1','0'] #adding key tag-bits and assigning valid and dirty bit as a list
                        self.LRU_dict[item_index].appendleft(tag_bits)
                        self.cache_misses += 1
                    elif access_type == 1:
                          self.LRU_Cache_dict[item_index][tag_bits]=['1','1']
                          self.LRU_dict[item_index].appendleft(tag_bits)
                          self.cache_misses += 1
                    #else:
                     #   print("### Code ERROR 1 ### {} {} {} ".format(access_type,tag_bits,item_index))
                elif len(self.LRU_Cache_dict[item_index]) < associativity and access_type != 2 and tag_bits in self.LRU_Cache_dict[item_index].keys(): #repeated data before cache fill
                    if access_type == 0 and self.LRU_Cache_dict[item_index][tag_bits][0] == '1':
                        self.LRU_Cache_dict[item_index][tag_bits][0]='1'
                        self.cache_hits += 1
                        
                    elif access_type == 1 and self.LRU_Cache_dict[item_index][tag_bits][0] == '1':
                        self.LRU_Cache_dict[item_index][tag_bits][0]='1'
                        self.LRU_Cache_dict[item_index][tag_bits][1]='1'
                        self.cache_hits += 1
                    self.LRU_dict[item_index].remove(tag_bits)
                    self.LRU_dict[item_index].appendleft(tag_bits)
                    
                elif len(self.LRU_Cache_dict[item_index]) < associativity and access_type == 2 and tag_bits in self.LRU_Cache_dict[item_index].keys():     # Increasing cache Hit.
                    if self.LRU_Cache_dict[item_index][tag_bits][1] == '1':     # cache not fill, same tagbits
                        self.write_backs += 1
                    del self.LRU_Cache_dict[item_index][tag_bits]
                    self.evictions += 1
                    self.LRU_dict[item_index].remove(tag_bits) 
                      
                elif len(self.LRU_Cache_dict[item_index]) == associativity  and tag_bits in self.LRU_Cache_dict[item_index].keys():
                    if access_type == 0:
                        self.cache_hits += 1
                        self.LRU_Cache_dict[item_index][tag_bits][0]='1' 
                        self.LRU_dict[item_index].remove(tag_bits)
                        self.LRU_dict[item_index].appendleft(tag_bits)
                    elif access_type == 1:
                        self.LRU_Cache_dict[item_index][tag_bits][0]='1'
                        self.LRU_Cache_dict[item_index][tag_bits][1]='1'
                        self.cache_hits += 1
                        self.LRU_dict[item_index].remove(tag_bits)
                        self.LRU_dict[item_index].appendleft(tag_bits)
                    elif access_type == 2:
                        if self.LRU_Cache_dict[item_index][tag_bits][1] == '1':
                           self.write_backs += 1
                        del self.LRU_Cache_dict[item_index][tag_bits]
                        self.evictions += 1
                        self.LRU_dict[item_index].remove(tag_bits)
                        
                elif len(self.LRU_Cache_dict[item_index]) == associativity  and tag_bits not in self.LRU_Cache_dict[item_index].keys():
                    if access_type == 0 or access_type == 1:
                        evict_TagBit =  self.LRU_dict[item_index].pop()
                        if self.LRU_Cache_dict[item_index][evict_TagBit][1] == '1':
                           self.write_backs += 1
                        del self.LRU_Cache_dict[item_index][evict_TagBit]
                        if access_type == 0:
                           self.LRU_Cache_dict[item_index][tag_bits] = ['1','0']
                        elif access_type == 1:
                            self.LRU_Cache_dict[item_index][tag_bits] = ['1','1']
                        self.LRU_dict[item_index].appendleft(tag_bits)
                        self.cache_misses += 1
                        self.evictions += 1
                    #if access_type == 2:
                        #print("#### No such address existing to invalidate, So nothing to do") 
                if len(self.LRU_Cache_dict[item_index]) > associativity:
                    print("### ERROR - Cache dic is more then associativity")
                #else:
                    #print("### Code ERROR 2 #### {} {} {}".format(access_type,tag_bits,self.LRU_Cache_dict[item_index].keys()))
            #else:
                #print("Cache Index not present in self.LRU_Cache_dict, ERROR!! WRONG ACCESS!!!")
        

    def process_1_bit_lru_cache(self):
        # Valid bit, dirty bit,status bit and tag bits as values and set bits as key
        template_list= ['0','0', '0', '0']
        line_list = []
        for i in range(0, self.num_ways):
            line_list.insert(i, ['0','0', '0', '0'])
        self.cache_dict = dict((bin_item, copy.deepcopy(line_list)) for bin_item in self.generate_binary(self.num_sets))
        #print(self.cache_dict)
        for item in self.access_list:
            address = self.hex_to_binary(item.split(' ')[1]) 
            address = address.strip(' ')
            new_address = ''
            if len(address) < 32:
                to_add_len = 32 - len(address)
                #print("to add:", to_add_len)
                for i in range(0,to_add_len+1):
                    new_address = new_address + '0'
                new_address = new_address + address
                address = new_address
            access_type = item.split(' ')[0]
            item_index = address[self.set_select_range[0]:self.set_select_range[1]]
            tag_bits = address[self.tag_select_range[0]:self.tag_select_range[1]]
#             if ' ' in item_index:
#                 print(item_index)
#                 print(address)
#                 raise Exception("Error")
            for line_item in self.cache_dict[item_index]:
                #item[0] - valid bit, item[1] - dirty bit, item[2] - status bit, item[3] - tag bits
                if line_item[3] == tag_bits and line_item[0]=='1':
                    # Cache hit!!
                    if access_type == '1':  # write access, setting the dirty bit
                        self.cache_hits += 1
                        line_item[1] = '1' # Make the dirty bit to 1
                        line_item[2] = '1'
                    elif access_type == '2':
                        if line_item[1] == '1': # invalidate access, clearing the valid bit, not a cache hit 
                            self.write_backs += 1
                        line_item[0] = '0' #we need to check dirty bit and wants to increase eviction and write back if dirty bit = 1
                        self.evictions += 1
                    elif access_type == '0':
                        self.cache_hits += 1
                        line_item[2] = '1' # Make the status bit to 1 even if already 1
                    break
            else: # Not a match, check for something with valid bit 0
                for line_item in self.cache_dict[item_index]:
                    if line_item[0] == '0' and access_type != '2': #Found an item with valid bit 0, hence update the same
                        item_to_modify = line_item
                        # Cache miss
                        item_to_modify[0]='1'
                        item_to_modify[2]='1'
                        item_to_modify[3]=tag_bits
                        if access_type=='1':
                            line_item[1]='1'
                        self.cache_misses += 1
                        break
                else: # Not able to find any line with valid bit 0, check if status bit is 0
                    # Replacement algorithm comes into picture
                    for line_item in self.cache_dict[item_index]: # Status bit 0 found. Replace this item
                        if line_item[2]=='0' and access_type != '2':
                            # Found a line which is not recently used to replace
                            self.cache_misses += 1    
                            line_item[2] = '1'
                            line_item[3] = tag_bits
                            self.evictions += 1
                            if line_item[1] == '1': # if the data is dirty should be written back to memory before evicting
                                self.write_backs += 1
                            if access_type == '1':
                                line_item[1] = '1'
                            break
                    else: # Status bit 0 not found, hence reset everything to 0
                        for line_item in self.cache_dict[item_index]:
                            line_item[2]='0' # Make all the status bits reset to 0
                        if access_type != '2':
                            line_item = self.cache_dict[item_index][0] #Take ths first item with status bit 0 and replace it
                            self.cache_misses += 1
                            line_item[3] = tag_bits
                            line_item[2] = '1'
                            self.evictions += 1
                            if line_item[1] == '1': # if the data is dirty should be written back to memory before evicting
                                self.write_backs += 1
                            if access_type == '1':
                                line_item[1] = '1'
    
    def process_1_bit_lru_cache_new1(self):
        # Valid bit, dirty bit,status bit and tag bits as values and set bits as key
        template_list= ['0','0', '0', '0']
        line_list = []
        for i in range(0, self.num_ways):
            line_list.insert(i, ['0','0', '0', '0'])
        self.cache_dict = dict((bin_item, copy.deepcopy(line_list)) for bin_item in self.generate_binary(self.num_sets))
        lineNum=0
        for item in self.access_list:
            lineNum += 1
            #print(lineNum,item)
            address = self.hex_to_binary(item.split(' ')[1])
            access_type = item.split(' ')[0]
            item_index = address[self.set_select_range[0]:self.set_select_range[1]]
            tag_bits = address[self.tag_select_range[0]:self.tag_select_range[1]].strip()
            #print(address,access_type,item_index,tag_bits)
            for line_item in self.cache_dict[item_index]:
                #item[0] - valid bit, item[1] - dirty bit, item[2] - status bit, item[3] - tag bits
                if line_item[3] == tag_bits and line_item[0]=='1':
                    # Cache hit!!
                    if access_type == '1':  # write access, setting the dirty bit
                        self.cache_hits += 1
                        line_item[1] = '1' # Make the dirty bit to 1
                        line_item[2] = '1'
                    elif access_type == '2':
                        if line_item[1] == '1': # invalidate access, clearing the valid bit, not a cache hit 
                            self.write_backs += 1
                            line_item[1] = '0'
                        line_item[0] = '0' #we need to check dirty bit and wants to increase eviction and write back if dirty bit = 1
                        line_item[1] = '0'
                        line_item[2] = '0'
                        line_item[3] = '0'
                        self.evictions += 1
                    elif access_type == '0':
                        self.cache_hits += 1
                        line_item[2] = '1' # Make the status bit to 1 even if already 1
                    break
            else: # Not a match, check for something with valid bit 0
                for line_item in self.cache_dict[item_index]:
                    if line_item[0] == '0' and access_type != '2': #Found an item with valid bit 0, hence update the same
                        item_to_modify = line_item
                        # Cache miss
                        line_item[0]='1'
                        line_item[2]='1'
                        line_item[3]=tag_bits
                        if access_type =='1':
                            line_item[1]='1'
                        self.cache_misses += 1
                        break
                else: # Not able to find any line with valid bit 0, check if status bit is 0
                    # Replacement algorithm comes into picture
                    for line_item in self.cache_dict[item_index]: # Status bit 0 found. Replace this item
                        if line_item[2]=='0' and access_type != '2':
                            # Found a line which is not recently used to replace
                            self.cache_misses += 1 
                            line_item[0] = '1'   
                            line_item[2] = '1'
                            line_item[3] = tag_bits
                            self.evictions += 1
                            if line_item[1] == '1': # if the data is dirty should be written back to memory before evicting
                                self.write_backs += 1
                                line_item[1] = '0'
                            if access_type == '1':
                                line_item[1] = '1'
                            break
                    else: # Status bit 0 not found, hence reset everything to 0
                        for line_item in self.cache_dict[item_index]:
                            line_item[2]='0' # Make all the status bits reset to 0
                        if access_type != '2':
                            line_item = self.cache_dict[item_index][0] #Take ths first item with status bit 0 and replace it
                            self.cache_misses += 1
                            line_item[0] = '1' 
                            line_item[3] = tag_bits
                            line_item[2] = '1'
                            self.evictions += 1
                            if line_item[1] == '1': # if the data is dirty should be written back to memory before evicting
                                self.write_backs += 1
                                line_item[1] = '0'
                            if access_type == '1':
                                line_item[1] = '1'
    def process_direct_mapped_cache(self):
        """
        process each entry in the input trace considering the cache as a direct mapped cache
        access type can be read, write or invalidate
        :return: None
        """
        # Valid bit, dirty bit, tag bits as values and set bits as key
        self.cache_dict = dict((item, ['0', '0', '0']) for item in self.generate_binary(self.num_sets))
        for item in self.access_list:
            #print("item: ", item)
            address = self.hex_to_binary(item.split(' ')[1])
            address = address.strip(' ')
            new_address = ''
            if len(address) < 32:
                to_add_len = 32 - len(address)
                #print("to add:", to_add_len)
                for i in range(0,to_add_len+1):
                    new_address = new_address + '0'
                new_address = new_address + address
                address = new_address
            #print("address: ", len(address))
            access_type = item.split(' ')[0]
            item_index = address[self.set_select_range[0]:self.set_select_range[1]]
            tag_bits = address[self.tag_select_range[0]:self.tag_select_range[1]]
            #print("Index: ", item_index)
            if self.cache_dict[item_index][0] == '0' and access_type != '2':
                # Cache miss :(
                self.cache_misses += 1
                self.cache_dict[item_index][0] = '1'   # valid bit is set
                self.cache_dict[item_index][2] = tag_bits
                if access_type == '1':  # write access, setting the dirty bit
                    self.cache_dict[item_index][1] = '1'
            elif self.cache_dict[item_index][0] == '1' and tag_bits != self.cache_dict[item_index][2] and access_type != '2':
                # Cache miss :(
                self.cache_misses += 1
                self.cache_dict[item_index][2] = tag_bits
                self.evictions += 1
                if self.cache_dict[item_index][1] == '1':
                    self.write_backs += 1
                if access_type == '1':
                    self.cache_dict[item_index][1] = '1'
            elif self.cache_dict[item_index][0] == '1' and tag_bits == self.cache_dict[item_index][2]:
                # valid bit is set and the tags match
                if access_type == '1':  # write access, setting the dirty bit
                    # Cache hit :)!!
                    self.cache_hits += 1
                    self.cache_dict[item_index][1] = '1'
                elif access_type == '2':  # invalidate access, clearing the valid bit, not a cache hit
                    self.cache_dict[item_index][0] = '0'
                    self.evictions += 1
                    if self.cache_dict[item_index][1] =='1':
                        self.write_backs += 1
                elif access_type == '0':
                    # Cache hit :)!!
                    self.cache_hits += 1

    @staticmethod
    def generate_binary(num):
        """
        Generates binary numbers from 0 to n
        :param num: Input integer
        :return: List of binary numbers
        """
        binary_keys = []
        max_len = len(bin(num-1)[2:])
        for i in range(num):
            b = bin(i)[2:]
            binary_keys.append('{:0{}b}'.format(i, max_len))
        return binary_keys

    @staticmethod
    def hex_to_binary(hex_string):
        """
        Converts a hexadecimal number into a 32bit binary string
        :param hex_string: Hexadecimal string
        :return: Binary string
        """
        return "{0:032b}".format(int(hex_string, 16))

    @staticmethod
    def decimal_to_binary(dec_string):
        """
        Converts a decimal to a binary string
        :param dec_string: decimal string
        :return: binary string
        """
        #return format(dec_string, "0b")
        return int(math.log2(dec_string))
