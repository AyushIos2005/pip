words = ["madam","hello","level"]

# words = "madam"
# print(words[::-1])
like=[i for i in words if i[::-1] == i]
# for i in words:
#     f = i
#     if i[::-1] == f:
#         like.append(i)

print(like)


