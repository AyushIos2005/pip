# # # i = 1

# # # while i<=10:
# # #     print(i)
# # #     if i == 6:
# # #         break
# # #     i += 1
# # # print("Hello")    


# # num = [1,2,3,4,5,6]

# # for n in num:
# #     print(n)
# #     if n == 3:
# #         break


# for i in range(1,5):
#     if i == 3:
#         pass
#     else:
        # print(i)

while True:
    user_input = input("Enter number : ")

    if user_input == 'q':
        break
    elif user_input.isdigit():
        print("Valid Number")

    else:
         pass
       