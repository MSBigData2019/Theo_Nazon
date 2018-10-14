import numpy as np

import regex as re

# Given an array of ints, return True if one of the first 4 elements
# in the array is a 9. The array length may be less than 4.
def array_front9(nums):
    num_array = np.array(nums)
    last_index = min(4, len(nums)) + 1
    shorted_array = num_array[:last_index]
    return np.any(shorted_array[shorted_array == 9])


list = [1,2,3,4,9]
print(array_front9(list))

def last2(string):
    pattern = string[-2:]
    print(pattern)
    return len(re.findall(pattern, string, overlapped=True))


string = "hixxxxxhihi"
print(last2(string))