# Zip
# names= ['Aman','Neha','Ravi']

# marks = [80,90]

# zip

# for name,marks in zip(names,marks):
#     print(name,marks)

# unzip

data = [("Aman",80),("Neha",90),("Ravi",70)]
names , marks = zip(*data)
print(list(names))
print(list(marks))


