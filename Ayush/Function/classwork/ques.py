'''
create a function that number n
return even number
'''

def even(a,b):
    li = 0
    for i in range(a,b+1):
        if i % 2 == 0:
            print(i,end=" ")
            li += 1

    return li        



n = int(input("Enter a number : "))
print(even(1,n))