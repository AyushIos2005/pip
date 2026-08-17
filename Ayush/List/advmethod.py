'''
append()





my_list = [1,2,3,4,5]
print("Before : ",my_list)
my_list.append("Yes")
print("After : ",my_list)
new_list = [1,2,3,4,5]
my_list.append(new_list)
print("After new list : ",my_list)


# Extend

a = [1,2]
a.extend([3,4])
print(a)

s = []
s.extend("abc")
print(s)

# insert[index,item]

nums = [10,20,30]

nums.insert(0,70)
print(nums)


# remove[item(value)]

name = ["Aman","Shaman","Naman","Yaman","Jaman"]

print("Before : ",name)
name.remove("Naman")
print("After : ",name)


# pop(index)
y = [10,20,30,40,50]

x = y.pop()

print(y)
print(x+1)


marks = [45,90,66,33,70,75,88]

marks.sort(reverse=True)
print(marks)


g = ["a","c","b"]
g.sort(reverse=True)
print(g)
'''

# Count()

c = [1,1,1,2,2,2,2,3,3,3,4,4,4,6,6,6]
print(c.count(2),c.count(3))