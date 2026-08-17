'''
1. Find Index of Element
    
    Problem: Return index of first occurrence of target.
'''

def idx_nums(t,target):
    return t.index(target)
    

nums = [5,79,7,79]
target = 79
t = tuple(nums)
i = idx_nums(t,target)
print(i)