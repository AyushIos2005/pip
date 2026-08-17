def second_largest(li):
    if len(li) < 2:
        return None

    # Use float('-inf') to handle lists with negative numbers
    max_v = float('-inf')
    max_2 = float('-inf')

    for num in li:
        if num > max_v:
            # The old max becomes the new second max
            max_2 = max_v
            max_v = num
        elif num > max_2 and num < max_v:
            # Update second max only if it's smaller than max
            max_2 = num
            
    return max_2 if max_2 != float('-inf') else None

li = [3, 1, 7, 5]
x = second_largest(li)
print("Second Largest Element in List:", x)
