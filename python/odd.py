def odd_numbers(nums: list) -> list:
    odd_nums = []

    for num in nums:
        if num % 2 != 0:
            odd_nums.append(num)

    return odd_nums

def list_comprehension_odd_numbers(nums: list) -> list:
    return [num for num in nums if num % 2 != 0]

