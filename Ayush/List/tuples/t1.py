import copy
# interview important

a=[1,2,[3,4]]
# a[3].append(10)
b=copy.deepcopy(a)

b[2].append(5)
# a[2].append(10)
print(a)
print(b)