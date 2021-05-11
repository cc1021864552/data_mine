import os
import time

from apriori import Apriori
from my_apriori import MY_Apriori


def data_reader(data_file):
    data_set = []
    with open(data_file, 'r') as f:
        for line in f:
            data_set.append(line.split()[3:])
    return data_set


def load_data_set():
    """
    Load a sample data set (From Data Mining: Concepts and Techniques, 3th Edition)
    Returns: 
        A data set: A list of transactions. Each transaction contains several items.
    """
    data_set = []
    for i in range(1, 100000):
        item = []
        for j in range(1, 11):
            item.append(10)
        data_set.append(item)

    return data_set


def test_raw_apriori(data_set, min_sup = 0.05):
    print("\nRaw Apriori")
    
    start = time.process_time()
    apriori = Apriori(data_set)
    frequent_itemsets = apriori.generate_L(min_sup)
    end = time.process_time()
    deltatime = end - start
    
    print ('{:>40}{:<20}'.format("Time(s): ", deltatime))
    print ('{:>40}{:<20}'.format("number of frequent itemsets: ", len(frequent_itemsets)))


def test_optimized_apriori(data_set, min_sup = 0.05):
    print("\nOptimized Apriori")
    
    start = time.process_time()
    m_apriori = MY_Apriori(data_set)
    m_frequent_itemsets = m_apriori.generate_L(min_sup)
    end = time.process_time()
    deltatime = end - start
    
    print ('{:>40}{:<20}'.format("Time(s): ", deltatime))
    print ('{:>40}{:<20}'.format("number of frequent itemsets: ", len(m_frequent_itemsets)))
    return


def test(test_count, data_set, data_set_length, average_item_per_trans, different_item_nums, min_sup):
    print('{:>40}{:<20}'.format("\nTest count: ", test_count))
    print('{:>40}{:<20}'.format("Numbers of transactions: ", data_set_length))
    print('{:>40}{:<20}'.format("Average items of per transaction: ", average_item_per_trans))
    print('{:>40}{:<20}'.format("Numbers of different items: ", different_item_nums))
    print('{:>40}{:<20}'.format("Min sup: ", min_sup))

    test_raw_apriori(data_set, min_sup)
    test_optimized_apriori(data_set, min_sup)

    return


if __name__ == "__main__":
    data_file = "../../data/test.data"
    data_set = data_reader(data_file)
    data_set_length = len(data_set)
    average_item_per_trans = 10
    different_item_nums = 100
    test(0, data_set, data_set_length, average_item_per_trans, different_item_nums, 0.005)
    # for i in list(range(1, 6)):
    #     test(i, data_set, data_set_length, average_item_per_trans, different_item_nums, 0.005+0.005*i)

    # test(1, data_set, data_length, 10, 100, 0.025)
    # test(2, data_set, data_length, 10, 100, 0.020)
    # test(3, data_set, data_length, 10, 100, 0.015)
    # test(4, data_set, data_length, 10, 100, 0.01)
    # test(5, data_set, data_length, 10, 100, 0.005)

    # test(data_set, min_sup = 0.01)
    # ./gen lit -ntrans 1 -tlen 10 -nitems 0.1 -npats 100 -patlen 4 -fname test -ascii
