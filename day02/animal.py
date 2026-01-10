class Animal:
    def __init__(self,name):
        self.name = name

class Dog(Animal):
    def __init__(self,name,hobby):
        super().__init__(name)
        self.hobby = hobby

    def describe(self):
        print(f"Dog Name:{self.name} , Dog Hobby:{self.hobby}")

class Cat(Animal):
    pass

Dog1 = Dog("Harry","sing")
Cat1 = Cat("Hermi")

Dog1.describe()
