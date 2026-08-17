from collections import Counter

def all_sumpair():
    nums = []

    size = int(input("Enter length of list: "))
    print("Enter list elements:")

    for i in range(size):
        nums.append(int(input()))
    print("List:", nums)
    target = int(input("Enter target value: "))

    nums.sort()
    left = 0
    right = len(nums) - 1
    pair = set()

    while left < right:
        curr_sum = nums[left] + nums[right]

        if curr_sum == target:
            pair.add((nums[left], nums[right]))
            left += 1
            right -= 1
        elif curr_sum < target:
            left += 1
        else:
            right -= 1

    print("All unique pairs:", list(pair))


def mat_transpose():
    row = int(input("Enter number of rows: "))
    col = int(input("Enter number of columns: "))

    matrix = []
    print("Enter elements row-wise:")
    for i in range(row):
        r = []
        for j in range(col):
            r.append(int(input()))
        matrix.append(r)

    print("\nOriginal Matrix:")
    for i in matrix:
        print(i)

    transpose = [list(r) for r in zip(*matrix)]

    print("\nTransposed Matrix:")
    for r in transpose:
        print(r)


def sort_list():
    size = int(input("Enter size of list: "))
    li = []

    print("Enter elements:")
    for i in range(size):
        li.append(int(input()))

    print("List:", li)

    # Bubble sort
    for p in range(size):
        for j in range(size - p - 1):
            if li[j] > li[j + 1]:
                li[j], li[j + 1] = li[j + 1], li[j]

    print("Sorted list:", li)


def missing_number():
    size = int(input("Enter size of array: "))
    li = []

    for i in range(size):
        li.append(int(input()))

    print("List:", li)

    expected_sum = sum(range(1, size + 1))
    actual_sum = sum(li)

    print("Missing number:", expected_sum - actual_sum)


def remove_occurence():
    nums = []
    size = int(input("Enter size of list: "))

    for i in range(size):
        nums.append(int(input()))

    print("List:", nums)

    target = int(input("Target: "))

    result = [x for x in nums if x != target]
    print("Output:", result)


def eq_tuple():
    li_1 = []
    li_2 = []

    size = int(input("Enter size of tuples: "))

    print("Enter tuple 1:")
    for i in range(size):
        li_1.append(int(input()))

    print("Enter tuple 2:")
    for i in range(size):
        li_2.append(int(input()))

    print("Tuple 1:", tuple(li_1))
    print("Tuple 2:", tuple(li_2))

    print(li_1 == li_2)


def sort_frequecy():
    nums = []
    size = int(input("Enter size of list: "))

    print("Enter elements:")
    for i in range(size):
        nums.append(int(input()))

    counts = Counter(nums)
    nums.sort(key=lambda x: (counts[x], -x))

    print("Output:", nums)


def find_sunlist(main, sub):
    n, m = len(main), len(sub)

    if m == 0:
        return True

    for i in range(n - m + 1):
        if main[i:i + m] == sub:
            return True

    return False


def genearte_pair():
    li = []
    size = int(input("Enter size of list: "))

    print("Enter elements:")
    for i in range(size):
        li.append(int(input()))

    print("All pairs:")
    for i in range(size):
        for j in range(i + 1, size):
            print((li[i], li[j]))


def count_inversion():
    li = []
    size = int(input("Enter size: "))

    for i in range(size):
        li.append(int(input()))

    count = 0
    for i in range(size):
        for j in range(i + 1, size):
            if li[i] > li[j]:
                count += 1

    print("Inversion count:", count)


# MENU
print("1.Find all pairs with Given Sum")
print("2.Matrix Transpose")
print("3.Sort Without Built-in")
print("4.Find Missing Number")
print("5.Remove All Occurrences")
print("6.Count Inversion")
print("7.Check if two Tuples are Equal")
print("8.Sort by Frequency")
print("9.Find Sublist")
print("10.Generate all pairs")
print("11.Exit")

while True:
    choice = int(input("Enter your choice: "))

    if choice == 1:
        all_sumpair()
    elif choice == 2:
        mat_transpose()
    elif choice == 3:
        sort_list()
    elif choice == 4:
        missing_number()
    elif choice == 5:
        remove_occurence()
    elif choice == 6:
        count_inversion()
    elif choice == 7:
        eq_tuple()
    elif choice == 8:
        sort_frequecy()
    elif choice == 9:
        main = [1, 2, 3, 4, 5]
        sub = [3, 4]
        print(find_sunlist(main, sub))
    elif choice == 10:
        genearte_pair()
    elif choice == 11:
        break
    else:
        print("Try again...")