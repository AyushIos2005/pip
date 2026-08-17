# "Set"

# rahul@gmail.com
# titu@gmail.com
# om@gmail.com
# komal@gmail.com
# rahul2gmail.com
# rahul2gmail.com

# creacteion 
'''
emails = {
   "rahul@gmail.com",
    "titu@gmail.com",
    "om@gmail.com",
    "komal@gmail.com",
    "rahul@gmail.com",
    "rahul@gmail.com"
}

print(emails)


num = [1,2,3,4,5,5,5,6,2,3,7,10]
print(num)
s=set(num)
print("Unqiue : ",s)


a = {1,"A",(2,3),(9,0),(2,1)} #correct
print(a)
b = {[1,23,3]} #incorrect avoid list inside set
print(b)

'''

s = {1,2,3}

s.add(4)
# print(s)
s.discard(2)
# print(s)

m = {1,2,3}
n = {3,4,5}
# union 
print(m | n)
# common value
print(m & n)
# extrat
print(m - n)





