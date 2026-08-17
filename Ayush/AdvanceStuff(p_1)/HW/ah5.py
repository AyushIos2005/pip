keys = ["a","b","c"]

values =[1,2,3]

# for key,value in enumerate(keys,values):
    # print(key,value)

output = {k: v for k, v in zip(keys, values)}
print(output)