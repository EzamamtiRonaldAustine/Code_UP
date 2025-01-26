def selection_sort(list1):
    index_length = range(0, len(list1))
    
    for i in index_length:
        min_value = i
        for j in range(i+1, len(list1)):
            if list1[j] < list1[min_value]:
                min_value = j
        
        if min_value != i:
            list1[min_value], list1[i] = list1[i], list1[min_value]
    
    return list1
print(selection_sort([0,5,4,3,2,1]))