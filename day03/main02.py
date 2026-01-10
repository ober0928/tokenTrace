def repeat(times):
    """带参数的装饰器：指定函数运行次数"""
    def decorator(func):
        def wrapper():
            for _ in range(times):
                func()
        return wrapper
    return decorator

@repeat(times=3)
def greet():
    print("Hello!")

greet() # 会打印三次 Hello!