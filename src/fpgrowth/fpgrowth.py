#! /usr/bin/env python3


# FP-growth算法虽然能高效地发现频繁项集，但是不能用于发现关联规则。
# FP-growth算法的执行速度快于Apriori算法，通常性能要好两个数量级以上。
# FP-growth算法只需要对数据集扫描两次，它发现频繁项集的过程如下：
#   1.构建FP树
#   2.从FP树中挖掘频繁项集


# 1.构建FP树(前缀树),步骤：
# 扫描数据集，对所有元素项的出现次数进行计数，去掉不满足最小支持度的元素项；
# 对每个集合进行过滤和排序，过滤是去掉不满足最小支持度的元素项，排序基于元素项的绝对出现频率来进行；
# 创建只包含空集合的根节点，将过滤和排序后的每个项集依次添加到树中，如果树中已经存在该路径，则增加对应元素上的值。
# 如果该路径不存在，则创建一条新路径。


# 2.从一棵FP树中挖掘频繁项集,步骤：
# 从FP树中获得条件模式基；
# 利用条件模式基，构建一个条件FP树；
# 迭代重复步骤1-2，直到树包含一个元素项为止。



from collections import defaultdict, Counter, deque
import math
import copy


class Node():
    # 本程序将节点之间的链接信息存储到项头表中，后续可遍历项头表添加该属性
    def __init__(self, item, count, parent):  
        self.item = item                # 该节点的项
        self.count = count              # 项的计数
        self.parent = parent            # 该节点父节点的id
        self.children = []              # 该节点的子节点的list


class FP():
    def __init__(self, minsup=0.5):
        self.minsup = minsup
        self.minsup_num = None                          # 支持度计数

        self.N = None
        self.item_head = defaultdict(list)              # 项头表
        self.fre_one_itemset = defaultdict(lambda: 0)   # 频繁一项集，值为支持度
        self.sort_rules = None                          # 项头表中的项排序规则，按照支持度从大到小有序排列
        self.tree = defaultdict()                       # fp树， 键为节点的id, 值为node
        self.max_node_id = 0                            # 当前树中最大的node_id, 用于插入新节点时，新建node_id
        self.fre_itemsets = []                          # 频繁项集
        self.fre_itemsets_sups = []                     # 频繁项集的支持度计数


# part 1: Build FPTree

    def __init_param(self, data):
        """
        Get data and build a fptree
        Args:
            data: raw data
        Return:
            None
        """
        self.N = len(data)
        self.minsup_num = math.ceil(self.minsup * self.N)
        
        self.__get_fre_one_itemset(data)
        
        self.__build_tree(data)

        return


    def __get_fre_one_itemset(self, data):
        """
        Get frequent 1-item set and frequences, and sort it
        Args:
            data: raw data
        Return:
            self.sort_rules:
            self.fre_one_itemset:
        """
        c = Counter()
        for t in data:
            c += Counter(t)
        for key, val in c.items():
            # print(val)
            # filtration
            if val >= self.minsup_num:
                self.fre_one_itemset[key] = val
        
        print("length of frequent 1-itemset: ", len(self.fre_one_itemset))
        # 频繁一项按照支持度降低的顺序排列，构建排序规则
        sort_keys = sorted(self.fre_one_itemset, key=self.fre_one_itemset.get, reverse=True)
        self.sort_rules = {k: i for i, k in enumerate(sort_keys)}

        return


    def __insert_item(self, parent, item):
        """
        Insert one new node into fp tree
        Args:
            parant: parant node's id
            item: new item need insert
        Return:
            next_node_id: inserted node's id
        """
        children = self.tree[parent].children
        for child_id in children:
            child_node = self.tree[child_id]
            if child_node.item == item:
                self.tree[child_id].count += 1
                next_node_id = child_id
                break
        else:  # 循环正常结束，表明当前父节点的子节点中没有项与之匹配，所以新建子节点，更新项头表和树
            self.max_node_id += 1
            next_node_id = copy.copy(self.max_node_id)                          # 注意self.max_node_id 是可变的，引用时需要copy
            self.tree[next_node_id] = Node(item=item, count=1, parent=parent)   # 更新树，添加节点
            self.tree[parent].children.append(next_node_id)                     # 更新父节点的孩子列表
            self.item_head[item].append(next_node_id)                           # 更新项头表

        return next_node_id


    def __build_tree(self, data):
        """
        Build FPTree and headers table
        Args:
            data: raw data
        Return:
            self.tree:
        """
        one_itemset = set(self.fre_one_itemset.keys())
        # create a vitural root
        self.tree[0] = Node(item=None, count=0, parent=-1)
        # tranverse dataset to create fp tree
        for t in data:
            t = list(set(t) & one_itemset)                          # filtration, 去除该事务中非频繁项
            if len(t) > 0:
                t = sorted(t, key=lambda x: self.sort_rules[x])     # 按照项的频繁程度从大到小排序
                parent = 0                                          # 每个事务都是从树根开始插起
                for item in t:
                    parent = self.__insert_item(parent, item)       # 将排序后的事务中每个项依次插入FP树
        return


# part 2: find all frequent itemsets


    def __get_path(self, pre_tree, condition_tree, node_id, suffix_items_count):
        """
        Get path which starts with given node and ends up with root, a complete condition path
        Args:
            pre_tree: FPtree
            condition_tree: a dict which contains all path
            node_id: current node's id
            suffix_items_count: suffix item's count
        Return:
            
        """
        # 根据后缀的某个叶节点的父节点出发，选取出路径，并更新计数。suffix_item_count为后缀的计数
        if node_id == 0:                                                            # 到根节点了
            return
        else:                                                                       
            if node_id not in condition_tree.keys():                                # current node 不在condition tree 中
                current_node = copy.deepcopy(pre_tree[node_id])
                current_node.count = suffix_items_count                             # 更新计数
                condition_tree[node_id] = current_node                              # 将current node 添加到condition tree中
            else:                                                                   # 若叶节点有多个，则路径可能有重复，计数叠加
                condition_tree[node_id].count += suffix_items_count
            
            node_id = condition_tree[node_id].parent
            self.__get_path(pre_tree, condition_tree, node_id, suffix_items_count)  # 递归构建路径
            return


    def __get_condition_tree(self, pre_tree, suffix_items_ids):
        """
        Build all posible conditon trees using provided suffix items' id
        Args:
            pre_tree: a complete fptree copy
            suffix_items_ids: a list, which contains ids that express one item in headers
        Return:
            condition_tree: all condition trees start with this specific suffix item
        """
        # 构建后缀为一个项的条件模式基。可能对应多个叶节点，综合后缀的各个叶节点的路径
        condition_tree = defaultdict()                                  # 字典存储条件FP树，值为父节点, {id: item}
        for suffix_id in suffix_items_ids:                              # 从各个后缀叶节点出发，综合各条路径形成条件FP树
            suffix_items_count = copy.copy(pre_tree[suffix_id].count)   # 叶节点计数
            node_id = pre_tree[suffix_id].parent                        # 注意条件FP树不包括后缀
            if node_id == 0:
                continue
            self.__get_path(pre_tree, condition_tree, node_id, suffix_items_count)
        
        return condition_tree


    def __extract_suffix_set(self, condition_tree, suffix_items):
        """
        Find frequent k-itemset from condition tree and suffix items
        Args:
            condition_tree:
            suffix_items:
        Return:
            new_suffix_items_list:
            new_item_head.values():
        """
        new_suffix_items_list = []                                          # 后缀中添加的新项
        new_item_head = defaultdict(list)                                   # 基于当前的条件FP树，更新项头表，新添加的后缀项
        item_sup_dict = defaultdict(int)

        for key, val in condition_tree.items():                             # condition tree: {id: item}
            item_sup_dict[val.item] += val.count                            # 对项出现次数进行统计
            new_item_head[val.item].append(key)

        for item, sup in item_sup_dict.items():
            if sup >= self.minsup_num:                                      # 若条件FP树中某个项是频繁的，则添加到后缀中
                current_item_set = [item] + suffix_items
                self.fre_itemsets.append(current_item_set)
                self.fre_itemsets_sups.append(sup)
                new_suffix_items_list.append(current_item_set)
            else:                                                           # 在条件模式基里面的支持度低于阈值，被我们删除
                new_item_head.pop(item)
        
        # dict.values() 方法返回 view 对象。这个视图对象包含列表形式的字典值。
        return new_suffix_items_list, new_item_head.values()


# part 3: user interface


    def get_fre_set(self, data):
        # 构建以每个频繁1项为后缀的频繁项集
        
        print("length of data: ", len(data))

        self.__init_param(data)
        
        suffix_items_list = []                                      # []
        suffix_items_id_list = []                                   # [[], []]
        
        for key, val in self.fre_one_itemset.items():
            suffix_items = [key]
            suffix_items_list.append(suffix_items)
            suffix_items_id_list.append(self.item_head[key])        # self.item_head[key] is a list
            self.fre_itemsets.append(suffix_items)
            self.fre_itemsets_sups.append(val)
        
        # pre_tree 是尚未去除任何后缀的前驱，若其叶节点的项有多种，则可以形成多种条件FP树
        pre_tree = copy.deepcopy(self.tree)  
        
        # call __dfs_search() to find all frequent itemsets
        self.__dfs_search(pre_tree, suffix_items_list, suffix_items_id_list)

        return


    def __dfs_search(self, pre_tree, suffix_items_list, suffix_items_id_list):
        """
        Build frequent k-itemsets
        Args:
            pre_tree: FPTree copy
            suffix_items_list: suffix items list which contain all frequent 1-items
            suffix_items_id_list: suffix item's id list, which may contain some ids
        Ruturn:
            self.fre_itemset: all frequent k-itemsets
        """
        # zip() 函数用于将可迭代的对象作为参数，将对象中对应的元素打包成一个个元组，然后返回由这些元组组成的列表。
        for suffix_items, suffix_items_ids in zip(suffix_items_list, suffix_items_id_list):
            # (suffix_items, [])
            condition_tree = self.__get_condition_tree(pre_tree, suffix_items_ids)
            new_suffix_items_list, new_suffix_items_id_list = self.__extract_suffix_set(condition_tree, suffix_items)
            # execute here, we get frequent 2-itemsets            

            # 如果后缀有新的项添加进来，则继续递归搜索, what does this mean?
            if new_suffix_items_list:
                self.__dfs_search(condition_tree, new_suffix_items_list, new_suffix_items_id_list)
        
        return


if __name__ == '__main__':
    data1 = [list('ABCEFO'), list('ACG'), list('ET'), list('ACDEG'), list('ACEGL'),
             list('EJ'), list('ABCEFP'), list('ACD'), list('ACEGM'), list('ACEGN')]
    data2 = [list('ab'), list('bcd'), list('acde'), list('ade'), list('abc'),
             list('abcd'), list('a'), list('abc'), list('abd'), list('bce')]
    data3 = [['r', 'z', 'h', 'j', 'p'], ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'], ['z'], ['r', 'x', 'n', 'o', 's'],
             ['y', 'r', 'x', 'z', 'q', 't', 'p'], ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]

    fp = FP(minsup=0.2)
    # interface
    fp.get_fre_set(data3)

    for itemset, sup in zip(fp.fre_itemsets, fp.fre_itemsets_sups):
        print(itemset, sup)
