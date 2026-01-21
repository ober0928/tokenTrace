def find_even_numbers(n):
    evens = []
    for i in range(n + 1):
        if i % 2 == 0:
            evens.append(i)
    return evens
print(find_even_numbers(10))

def greetings (name = 'Peter'):
    message = name + ', welcome to Python for Everyone!'
    return message
print(greetings())
print(greetings('Asabeneh'))

'''
**关键字不定长参数（kwargs）
在 Python 中，双星号 ** 的作用是将函数调用时传入的“关键字参数”打包成一个字典 (Dictionary)。
'''
def arbitrary_named_args(**args):
    print("I received an arbitrary number of arguments, totaling", len(args))
    print("They are provided as a dictionary in my function:", type(args))
    print("Let's print them:")
    for k, v in args.items():
        print(" * key:", k, "value:", v)
arbitrary_named_args(name="Gemini", version="3.0", language="Python")

def are_all_unique(lst):
    return len(lst) == len(set(lst))
print(are_all_unique([1,2,3,4,5,5]))


def is_same_type(lst):
    if not lst:
        return True
    first_type = type(lst[0])
    return all(isinstance(item, first_type) for item in lst)
print(is_same_type([1,2,3,4,5,5.3]))