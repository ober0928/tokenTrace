day04
# python Learning

# 1.exception handling
try:
    number = int(input("Enter a number"))
    print(1 / number)
except ZeroDivisionError:
    print("can’t divide by zero number)
finally:
    print("ok")

# 2.file detection
import os

# 3.multithreading
import threading
import time

def walk_dog(name)
    time.sleep(8)
    print(f"Finish walking {name}")

def take_out_trash()
    time.sleep()
    print("you take out the trash)

def get_mail()
    time.sleep(4)
    print("you get the mail")

chore1 = threading.Thread(target=walk_dog, args("Scooby",))
chore1.start()
``` Creat thread```
chore2 = threading.Thread(target=take_out_trash)
chore2.start()

chore2 = threading.Thread(target=get_mail)
chore2.start()

chore1.join()
chore2.join()
chore3.join()
```Creat join method, wait these thread fish to continuing the next step```
print("All task was done")

# 4.request api
import request

base_url = "https://pokeapi.co/api/v2"

def get_pokemin_info(name):
    url = f"{base_url}/pokemon/{name}
    response = request.get(url)

    if response.satsus_code == 200:
        print("Data recived")
    else:
    print(f"Failed {response.status_code}"

pokemon_name = "pikachu"
get_pokemin_info(pokemon_name)