day03
# python Learning
1. Python developers use snake case(snake_case) variable naming convention. 
```
first_name = 'Asabeneh'
last_name = 'Yetayeh'
```
2. Multiple variables can also be declared in one line:
```
first_name, last_name, country, age, is_married = 'Asabeneh', 'Yetayeh', 'Helsink', 250, True
```
3. staticmethod not need creat any object from that class
```
@staticmethod
def is_vaild_position(position):
    vaild_position = ["Manager", "cook"]
    return position in vaild_position
```
4. Classmethod only access class attributes
```
class Student:
    count = 0  # 类属性，初始值为0

    def __init__(self, name):
        self.name = name
        Student.count += 1  # 每创建一个实例，计数器加1

    @classmethod
    def get_count(cls):
        # 这里的 cls 就是 Student 类
        return f"Total # of student: {cls.count}"

# 使用过程：
s1 = Student("Alice")
s2 = Student("Bob")
print(Student.get_count())  # 输出: Total # of student: 2
```
use the staticmethod to achieve the same effect
```
@staticmethod
def get_count_static():
    return f"总人数是: {Student.count}" # 必须手动指定类名
```
5. Different between staticmethod and Classmethod
    类方法：就像工厂的经理，他手里拿着工厂的公章（cls），可以查看工厂的订单总量、修改工厂的生产标准。

    静态方法：就像工厂门口的一台计算器，它放在工厂里是因为方便工人使用，但它本身不需要知道工厂的任何秘密，它只负责完成特定的计算任务。
```
class Employee:
    base_salary = 5000  # 类变量：基本工资

    def __init__(self, name):
        self.name = name

    # --- 类方法案例 ---
    @classmethod
    def set_base_salary(cls, amount):
        """
        这个方法像经理：它可以修改全公司的基本工资
        """
        cls.base_salary = amount
        return f"全公司基本工资已调整为: {cls.base_salary}"

    # --- 静态方法案例 ---
    @staticmethod
    def is_work_day(day):
        """
        这个方法像工具：它只判断周几，不需要知道公司任何信息
        """
        # 假设 5 是周六，6 是周日
        if day == 5 or day == 6:
            return False
        return True

# --- 实际调用 ---

# 1. 调用类方法：直接改变了类的属性
print(Employee.set_base_salary(6000)) 

# 2. 调用静态方法：执行一个独立的逻辑判断
print(f"今天加班吗？ {'不加班' if Employee.is_work_day(5) else '要加班'}")
```
6. @property 装饰器是一个非常优雅的工具。它的核心作用是：把一个方法变成属性来调用。
在访问数据时，表面上看起来是在读一个普通变量，但背后其实执行了一段函数逻辑。
```
class Employee:
    def __init__(self, salary):
        self._salary = salary

    # 1. Getter: 获取薪水
    @property
    def salary(self):
        return self._salary

    # 2. Setter: 修改薪水（带有逻辑检查）
    @salary.setter
    def salary(self, value):
        if value < 0:
            raise ValueError("薪水不能为负数！")
        print(f"薪水已更新为: {value}")
        self._salary = value

# 使用
emp = Employee(5000)
emp.salary = 6000  # 触发 setter，正常更新
# emp.salary = -100 # 会直接抛出异常，起到保护作用
```
7. 在 Python 中，装饰器（Decorator）的本质是一个闭包函数，它接收一个函数作为参数，并返回一个新的函数。\
如果你提到“给装饰器添加方法”，通常有两种理解：一是给带参数的装饰器传递配置，二是装饰器本身是一个类，并在类中定义方法。
```
def my_decorator(func):
    def wrapper(*args, **kwargs): #*args, **kwargs,用于包装函数可以接收任何数量的参数和关键词
        print("--- 执行前：检查权限 ---") 
        result = func(*args, **kwargs)
        print("--- 执行后：清理现场 ---")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    print(f"你好, {name}!")

say_hello("Gemini")
```
```
def repeat(times):
    """带参数的装饰器：指定函数运行次数"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(times=3)
def greet():
    print("Hello!")

greet() # 会打印三次 Hello!
```