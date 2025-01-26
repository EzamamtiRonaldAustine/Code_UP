def insertion(list1):
    index_length = range(1, len(list1))
    for i in index_length:
        value_to_sort = list1[i]
        
        while list1[i-1] > value_to_sort and i>0:
            list1[i], list1[i-1] = list1[i-1], list1[i]
            i = i-1
    return list1
            
    

print(insertion([0,5,4,3,2,1]))       