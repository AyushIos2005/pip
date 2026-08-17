# x ={
#     "a" : [1,2,3],
#     "b" : [1,2,3]
# }
# print(x["a"]) 
# 

student = {} #empty

student["id"] = 101
student["name"] = "Pavan"
student["age"] = 25
student["marks"] = 80

# print(student)

student.update({
    "city" : "Kolkata",
    "Grade" : "A",
    "id":102
})
# print("After Update: ",student) 


#read - key 

# print(student["name"])
# print(student["id"])
# print(student["age"])


for key,value in student.items():
    print(key," : ",value)

# Update

# student["id"] : 102
# delete

# del student[""]
student.pop("id")
student.pop("kon",None)

print(student)