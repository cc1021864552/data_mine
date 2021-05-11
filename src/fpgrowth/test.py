#! /usr/bin/env python3

from fpgrowth import FP 
import time

def test(data_file_name):
    data_set = []
    with open(data_file_name, 'r') as f:
        for line in f:
            data_set.append(line.split()[3:])
    return data_set



if __name__ == "__main__":
    data_file_name = "../../data/test.data"
    data_set = test(data_file_name)
    # print("length of data set: ", len(data_set))
    fp = FP(minsup=0.01)

    start_time = time.process_time()
    fp.get_fre_set(data_set)
    end_time = time.process_time()
    
    print("time: ", end_time-start_time)
    print("length of frequent itemsets: ", len(fp.fre_itemsets))
    
    # for itemset, sup in zip(fp.fre_itemsets, fp.fre_itemsets_sups):
    #     print(itemset, sup)
