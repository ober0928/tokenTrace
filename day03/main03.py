class Student:
    count = 0  # 类属性，初始值为0

    def __init__(self, name):
        self.name = name
        Student.count += 1  # 每创建一个实例，计数器加1

    @classmethod
    def get_count(cls):
        # 这里的 cls 就是 Student 类
        return f"Total # of student: {cls.count}"
        #return f"Total # of student: {Student.count}"效果一样

# 使用过程：
s1 = Student("Alice")
s2 = Student("Bob")
print(Student.get_count())  # 输出: Total # of student: 2