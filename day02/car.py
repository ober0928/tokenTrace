class Car:

    car_type = "Mercedes"
    # outside variable can use by all

    car_num = 0

    def __init__(self, model, year):
        self.model = model
        self.year = year
        Car.car_num += 1
        #can calculate how many car object there are

    def describeCar(self):
        print(f"model is:{self.model} ,year is:{self.year}")
