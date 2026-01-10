class Student:
    def __init__(self, score):
        self._score = score

    @property
    def score(self):
        """Getter: 像读取属性一样读取值"""
        return self._score

    @score.setter
    def score(self, value):
        """Setter: 像给属性赋值一样进行检查"""
        if 0 <= value <= 100:
            self._score = value
        else:
            raise ValueError("分数必须在0-100之间")

# 使用时：
s = Student(90)
s.score = 90             # 像普通变量一样赋值，但触发了 setter 的检查
print(s.score)           # 像普通变量一样读取，但触发了 getter


class Student:
    def __init__(self, score):
        self._score = score

    # 获取分数的“动作”
    def get_score(self):
        return self._score

    # 设置分数的“动作”，带检查
    def set_score(self, value):
        if 0 <= value <= 100:
            self._score = value
        else:
            print("错误：分数必须在0-100之间")

# 使用时：
s = Student(60)
s.set_score(90)          # 必须调用方法
print(s.get_score())     # 必须调用方法

