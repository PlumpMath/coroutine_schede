# coding: utf-8
#a = [973, 973, 131, 326, 714, 904, 424, 256, 982, 142]
a = [973, 326, 714, 904, 424, 256, 973]
# -*- coding: utf-8 -*-

import random


def quick_sort(array, left, right):
    if left >= right:
        return
    index = left
    value_tmp = array[index]
    i, j = left,right
    start_right = index
    while i < j:
        while j > i:
            if array[j] < value_tmp:
                break
            j -= 1
        array[i] = array[j]

        while i < j:
            if array[i] >= value_tmp:
                break
            i += 1
        array[j] = array[i]

    array[i] = value_tmp
    print("array: ", array, left, i, right,value_tmp)
    quick_sort(array, left, i)
    quick_sort(array, i + 1, right)

def quick_sort_three_array(array):
    if len(array) <= 1:
        return array
    left_array, mid_array, right_array = [], [], []
    value = array[0]
    for ele in array:
        if ele < value:
            left_array.append(ele)
        elif ele == value:
            mid_array.append(ele)
        else:
            right_array.append(ele)
    left_array = quick_sort_three_array(left_array)
    right_array = quick_sort_three_array(right_array)

    return left_array + mid_array + right_array


if __name__ == '__main__':
    # quick_sort(a, 0, len(a) - 1)
    index = 1
    while index < 1000:
        a = [random.randint(0, 1000) for i in range(10)]
        # print("bef  a", a)
        b = a.copy()
        a = quick_sort_three_array(a)
        # print("a", a)
        b = sorted(b)
        assert a == b
        index += 1
