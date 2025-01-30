# quick sort makes one value as the pivot and the remaining values are compared to it..
def quick_sort(list1):
    length = len(list1)
    if length <= 1:
        return list1
    else:
        pivot = list1.pop()
    
    num_greater = []
    num_lower = []
    
    for num in list1:
        if num > pivot:
           num_greater.append(num)
        else:
            num_lower.append(num)
    return quick_sort(num_lower) + [pivot] + quick_sort(num_greater)

print(quick_sort([0,5,4,3,2,1]))