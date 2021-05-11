from datetime import datetime

class Apriori():

    def __init__(self, dataset):
        self.dataset = dataset                      # 数据集
        self.support_data = {}                      # (item, support)
        self.freq_itemsets = []                     # 所有的频繁项集
        self.big_rule_list = []                     # 所有的强关联规则集
        self.t_num = float(len(self.dataset))       # 数据集的大小

        # self.count = 0


    def __create_C1(self):
        """
        Create frequent candidate 1-itemset C1 by scaning data set.
        Args:
            data_set: A list of transactions. Each transaction contains several items.
        Returns:
            C1: A set which contains all frequent candidate 1-itemsets
        """
        C1 = set()
        for t in self.dataset:
            for item in t:
                item_set = frozenset([item])
                C1.add(item_set)
        return C1


    def __is_apriori(self, Ck_item, Lksub1):
        """
        Judge whether a frequent candidate k-itemset satisfy Apriori property.
        => if A is a frequent itemset, all subsets of A are frequent itemsets.
        => if A is not a frequent itemset, all supersets of A are frequent itemsets.
        Args:
            Ck_item: a frequent candidate k-itemset in Ck which contains all frequent candidate k-itemsets.
            Lksub1: Lk-1, a set which contains all frequent (k-1)-itemsets.
        Returns:
            True: satisfying Apriori property.
            False: Not satisfying Apriori property.
        """
        for item in Ck_item:
            sub_Ck = Ck_item - frozenset([item])
            # rule two: if A is not a frequent itemset, all supersets of A are frequent itemsets.
            if sub_Ck not in Lksub1:
                return False
        return True


    def __create_Ck(self, Lksub1, k):
        """
        Create Ck, a set which contains all all frequent candidate k-itemsets by Lk-1's own connection operation.
        Args:
            Lksub1: Lk-1, a set which contains all frequent (k-1)-itemsets.
            k: the item number of a frequent itemset.
        Return:
            Ck: a set which contains all all frequent candidate k-itemsets.
        """
        Ck = set()
        len_Lksub1 = len(Lksub1)
        list_Lksub1 = list(Lksub1)

        # temp_count = self.count

        for i in range(len_Lksub1):
            for j in range(1, len_Lksub1):
                l1 = list(list_Lksub1[i])
                l2 = list(list_Lksub1[j])
                l1.sort()
                l2.sort()
                if l1[0:k-2] == l2[0:k-2]:
                    # self.count += 1
                    Ck_item = list_Lksub1[i] | list_Lksub1[j]
                    if self.__is_apriori(Ck_item, Lksub1):
                        Ck.add(Ck_item)
        
        # print("compare counts: ", self.count-temp_count)
        # print("Ck's length: ", len(Ck))
        
        return Ck


    def __generate_Lk_by_Ck(self, Ck, min_sup):
        """
        Generate Lk by executing a delete policy from Ck.
        Args:
            data_set: A list of transactions. Each transaction con tains several items.
            Ck: A set which contains all all frequent candidate k-itemsets.
            min_sup: The minimum support.
            support_data: A dictionary. The key is frequent itemset and the value is support.
        Returns:
            Lk: A set which contains all all frequent k-itemsets.
        """
        Lk = set()
        item_count = {}
        for t in self.dataset:
            for item in Ck:
                # check whether item is t's subset
                if item.issubset(t):
                    if item not in item_count:
                        item_count[item] = 1
                    else:
                        item_count[item] += 1

        for item in item_count:
            if (item_count[item] / self.t_num) >= min_sup:
                Lk.add(item)
                self.support_data[item] = item_count[item] / self.t_num
        return Lk


    def generate_L(self, min_sup):
        """
        Generate all frequent itemsets.
        Args:
            data_set: A list of transactions. Each transaction contains several items.
            k: Maximum number of items for all frequent itemsets.
            min_sup: The minimum support.
            min_conf: The minium confidence.
        Returns:
            L: The list of Lk.
            rules_list: The big rules of all frequent itemsets.
            support_data: A dictionary. The key is frequent itemset and the value is support.
        """
        C1 = self.__create_C1()
        print("C1's length: ", len(C1))
        L1 = self.__generate_Lk_by_Ck(C1, min_sup)
        
        Lksub1 = L1.copy()
        for lk_i in Lksub1:
            self.freq_itemsets.append((lk_i, self.support_data[lk_i]))
        i = 2

        while True:
            Ci = self.__create_Ck(Lksub1, i)
            Li = self.__generate_Lk_by_Ck(Ci, min_sup)
            
            Lksub1 = Li.copy()
            if len(Lksub1) == 0:
                break
            for lk_i in Lksub1:
                self.freq_itemsets.append((lk_i, self.support_data[lk_i]))
            i += 1
        
        return self.freq_itemsets
    

    def generate_big_rules(self, min_conf):
        """
        Generate big rules from frequent itemsets.
        Args:
            L: all frequent itemsets.
            support_data: A dictionary. The key is frequent itemset and the value is support.
            min_conf: Minimal confidence.
        Returns:
            big_rule_list: A list which contains all big rules. Each big rule is represented as a 3-tuple.
        """
        sub_set_list = []

        # tranverse all frequent itemsets
        for i in range(0, len(L)):
            for freq_set in L[i]:
                for sub_set in sub_set_list:
                    if sub_set.issubset(freq_set):
                        # calculate confidence
                        conf = support_data[freq_set] / support_data[freq_set-sub_set]
                        big_rule = (freq_set-sub_set, sub_set, conf)
                        if conf >= min_conf and big_rule not in big_rule_list:
                            big_rule_list.append(big_rule)
                sub_set_list.append(freq_set)
        return self.big_rule_list
